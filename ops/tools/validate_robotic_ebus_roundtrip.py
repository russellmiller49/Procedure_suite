#!/usr/bin/env python3
"""Exercise two separate synthetic applications without transferring any local database.

Run with the clinical application's test environment. Only a coded SubmissionBatch
crosses between applications. All identities, keys, notes and approvals are synthetic.
"""

import argparse
import importlib.util
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from uuid import uuid4


def helpers(name, root):
    spec = importlib.util.spec_from_file_location(name, root / "tests/conftest.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def checked(response, code=200):
    if response.status_code != code:
        raise AssertionError(f"synthetic request failed: {response.status_code} {response.text}")
    return response.json()


def validate(clinical_root, national_root):
    for path in (
        clinical_root / "src",
        national_root / "src",
        clinical_root / "vendor/ip_registry_contracts/src",
        clinical_root / "vendor/ip_registry_engine/src",
    ):
        sys.path.insert(0, str(path))
    c = helpers("clinical_validation_helpers", clinical_root)
    n = helpers("national_validation_helpers", national_root)
    from clinical.main import create_app as clinical_app
    from clinical.models import LocalPolicy
    from national.main import create_app as national_app
    from national.models import PolicyEpoch
    from ip_registry_contracts.models import ClinicalRevision, Permissions
    from registry_platform.db import Base

    with TemporaryDirectory(prefix="ipr-focused-roundtrip-") as temporary:
        root = Path(temporary)
        croot, nroot = root / "clinical", root / "national"
        croot.mkdir()
        nroot.mkdir()
        ns, profile = n.make_settings(nroot, "national")
        ns.database_url = "sqlite:///" + str(nroot / "national.db")
        national = national_app(ns)
        Base.metadata.create_all(national.state.engine)
        with national.state.sessions.begin() as db:
            db.add(PolicyEpoch(id=1, value=1))
        operator = n.authenticated(national, ["national_operator", "national_analyst"])
        permissions = {
            "national_contribution": True,
            "institutional_benchmarking": True,
            "regional_comparisons": True,
        }
        site, facility, representative, submitter = n.institution(national, operator, permissions)

        cs, _ = c.make_settings(croot)
        cs.site_id = site
        cs.database_url = "sqlite:///" + str(croot / "clinical.db")
        # A single synthetic signed profile is independently verified by both boundaries.
        cs.profile_file = ns.profile_file
        cs.profile_verification_key_file = ns.profile_verification_key_file
        clinical = clinical_app(cs)
        Base.metadata.create_all(clinical.state.engine)
        with clinical.state.sessions.begin() as db:
            db.add(LocalPolicy(site_id=site, revision=1, payload=Permissions().model_dump_json()))
        reviewer = c.authenticated(
            clinical, ["abstractor", "reviewer", "steward", "institution_representative", "analyst"]
        )
        patient, encounter, procedure, values = c.create_case(reviewer)
        original = checked(reviewer.get(f"/api/v1/procedures/{procedure}"))
        target, specimen, pathology = (str(uuid4()) for _ in range(3))
        values.update(
            procedures=[
                {
                    "category": "robotic_bronchoscopy",
                    "performance": "performed",
                    "completion": "completed",
                }
            ],
            case_details={"indication": "LOCAL_NARRATIVE_CANARY", "age_at_procedure_years": 95},
            targets=[
                {
                    "target_id": target,
                    "site": "lung",
                    "lobe": "RUL",
                    "anatomic_label": "LOCAL_TARGET_CANARY",
                    "prespecified_biopsy_target": True,
                    "diagnostic_attempted": True,
                    "specimen_obtained": True,
                }
            ],
            specimens=[
                {
                    "specimen_id": specimen,
                    "target_id": target,
                    "specimen_label": "LOCAL_SPECIMEN_CANARY",
                    "target_attribution_status": "attributed",
                }
            ],
            pathology_results=[
                {
                    "pathology_result_id": pathology,
                    "specimen_id": specimen,
                    "target_id": target,
                    "result_scope": "index",
                    "result_status": "final",
                    "index_result_class": "specific_malignant",
                    "diagnosis_text": "LOCAL_DIAGNOSIS_CANARY",
                }
            ],
            follow_up=[],
        )
        context = {"patient_id": patient, "encounter_id": encounter}
        ClinicalRevision.model_validate(values)
        draft = checked(
            reviewer.post(
                f"/api/v1/procedures/{procedure}/revisions",
                json={"expected_version": 3, **context, "values": values},
            ),
            201,
        )
        during = checked(reviewer.get(f"/api/v1/procedures/{procedure}"))
        assert during["approved_id"] == original["approved_id"]
        checked(
            reviewer.post(
                f"/api/v1/procedures/{procedure}/approve",
                json={"expected_version": 4, **context, "revision_id": draft["revision_id"]},
            )
        )
        checked(
            reviewer.put(
                "/api/v1/participation",
                json={
                    "expected_revision": 1,
                    "authorization_reference": str(uuid4()),
                    "permissions": permissions,
                },
            )
        )
        checked(
            reviewer.put(
                f"/api/v1/patients/{patient}/national-eligibility",
                json={
                    "expected_version": 1,
                    "national_allowed": True,
                    "permitted_use_reference": str(uuid4()),
                },
            )
        )
        staged = checked(
            reviewer.post(
                f"/api/v1/procedures/{procedure}/national-stage",
                json={
                    "expected_version": 5,
                    "facility_id": facility,
                    "disclosure_review_reference": str(uuid4()),
                },
            ),
            201,
        )
        checked(reviewer.post(f"/api/v1/outbox/{staged['id']}/release"))
        exporter = c.machine_client(clinical, site, "outbox_dispatch")
        (batch,) = checked(exporter.get("/api/v1/outbox-dispatch"))
        serialized = json.dumps(batch)
        assert "CANARY" not in serialized and "2025-01-01" not in serialized
        assert all(
            identifier not in serialized
            for identifier in (patient, encounter, procedure, target, specimen, pathology)
        )
        (record,) = batch["records"]
        assert record["age_band"] == "90_plus"
        assert record["pathology_results"][0]["target_id"] == record["targets"][0]["target_id"]
        receipt = checked(submitter.post("/api/v1/submissions", json=batch))
        assert receipt["records"][0]["outcome"] == "accepted"
        assert checked(submitter.post("/api/v1/submissions", json=batch)) == receipt
        assert checked(submitter.get(f"/api/v1/submissions/{staged['id']}/receipt")) == receipt
        assert (
            checked(exporter.post("/api/v1/outbox-receipts", json=receipt))["state"]
            == "acknowledged"
        )
        assert checked(exporter.get("/api/v1/outbox-dispatch")) == []

        queued = checked(
            representative.post(
                "/api/v1/reports/jobs",
                json={
                    "definition": {
                        "measure_id": "robotic_ebus_launch",
                        "version": "0.2.0",
                        "registry_profile": "robotic_ebus_v1",
                        "population": "institutional_benchmark",
                        "year": 2025,
                    },
                    "purpose_reference": str(uuid4()),
                },
            ),
            202,
        )
        report_id = checked(operator.post(f"/api/v1/reports/jobs/{queued['job_id']}/execute"))[
            "report_id"
        ]
        report = checked(representative.get(f"/api/v1/reports/{report_id}"))
        assert report["own"]["strict_index_yield"]["denominator"] == 1
        assert report["own"]["strict_index_yield"]["numerator"] == 1
        assert report["own"]["counts"]["safety_30_day_outcome_unassessed"] == 1
        assert report["peers"]["status"] == "unavailable"
        checked(
            representative.put(
                "/api/v1/participation",
                json={
                    "expected_revision": 2,
                    "authorization_reference": str(uuid4()),
                    "permissions": {"national_contribution": False},
                },
            )
        )
        assert representative.get(f"/api/v1/reports/{report_id}").status_code == 409
        for client in (operator, representative, submitter, reviewer, exporter):
            client.close()
        clinical.state.engine.dispose()
        national.state.engine.dispose()
        return {
            "status": "passed",
            "contract_version": "0.2.0",
            "registry_profile": "robotic_ebus_v1",
            "synthetic_only": True,
            "separate_stores": True,
            "immutable_approval_preserved": True,
            "national_canaries_excluded": True,
            "ids_and_relationships_remapped": True,
            "signed_profile_verified": True,
            "intake_receipt_replay_idempotent": True,
            "local_receipt_acknowledged": True,
            "strict_index_yield_linked": True,
            "missing_safety_not_negative": True,
            "policy_revocation_invalidates_report": True,
            "independent_qualification": "pending",
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clinical-root", type=Path, required=True)
    parser.add_argument("--national-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = validate(args.clinical_root.resolve(), args.national_root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
