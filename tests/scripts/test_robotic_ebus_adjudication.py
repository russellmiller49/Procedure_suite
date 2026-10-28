"""Adjudication integrity and release gates; fixtures are never clinical evidence."""

import json

import pytest

from ops.tools import qualify_robotic_ebus as qualification
from ops.tools import robotic_ebus_adjudication as workflow

TEXT = (
    "🫁 Procedure: EBUS. Station 7 short axis 8 mm, sampled with 3 passes. "
    "Station 4L visualized but not sampled. RUL target localized using radial EBUS. "
    'No complications. <script>alert("x")</script>\n'
)


def corpus_at(path):
    path.mkdir()
    rows = {}
    for split in workflow.SPLITS:
        text = TEXT if split == "test" else f"Unique {split} case without source equivalence."
        row = {
            "document_id": split,
            "family_id": "family-" + split,
            "text": text,
            "text_sha256": workflow.digest(text),
            "split": split,
            "platform": "Ion",
            "sources": ["source.txt"],
            "generator_metadata": {"hidden_outcome": "SECRET"},
            "prior_training_overlap": split == "regression",
        }
        rows[split] = row
        (path / f"{split}.jsonl").write_text(json.dumps(row) + "\n")
    workflow.save(
        path / "split_manifest.json",
        {
            "profile": "robotic_ebus_v1",
            "documents": 4,
            "splits": {r["family_id"]: r["split"] for r in rows.values()},
            "artifacts": {
                f"{s}.jsonl": workflow.digest((path / f"{s}.jsonl").read_bytes())
                for s in workflow.SPLITS
            },
        },
    )
    return path


@pytest.fixture
def setup(tmp_path):
    corpus = corpus_at(tmp_path / "corpus")
    packet = tmp_path / "packet"
    workflow.packet(corpus, packet)
    rows, manifest = workflow.load_packet(corpus, packet)
    return corpus, packet, rows, manifest


def review_at(directory, manifest, reviewer="reviewer-a"):
    directory.mkdir()
    case = next(iter(manifest["cases"]))
    review = {
        "case_id": case,
        "reviewer_id": reviewer,
        "clinical_expertise": "test fixture",
        "blinded": "true",
        "independent": "true",
        "completed_at": "2026-10-10T10:00:00-07:00",
        "resolution_notes": "",
    }
    definitions = [
        ("station", "7", "7", "affirmed"),
        ("short_axis_mm", "short axis 8 mm", "8", "affirmed"),
        ("pass_count", "3 passes", "3", "affirmed"),
        ("sampled", "sampled with 3 passes", "sampled", "affirmed"),
        ("station", "4L", "4L", "affirmed"),
        ("observed_not_sampled", "visualized but not sampled", "observed_not_sampled", "affirmed"),
        ("target", "RUL", "RUL", "affirmed"),
        ("localization", "radial EBUS", "radial_EBUS", "affirmed"),
        ("procedure", "Procedure: EBUS", "procedure", "affirmed"),
        ("safety", "No complications", "absent", "negated"),
    ]
    spans = [
        {
            "case_id": case,
            "span_id": str(i),
            "start": str(TEXT.index(text)),
            "end": str(TEXT.index(text) + len(text)),
            "text": text,
            "label": label,
            "normalized": value,
            "assertion": assertion,
        }
        for i, (label, text, value, assertion) in enumerate(definitions)
    ]
    pairs = [(0, 1), (0, 3), (4, 5), (0, 2), (6, 7), (8, 9)]
    relations = [
        {
            "case_id": case,
            "relationship_id": str(i),
            "field": field,
            "source_span_id": str(pair[0]),
            "target_span_id": str(pair[1]),
        }
        for i, (field, pair) in enumerate(zip(workflow.FIELDS, pairs, strict=True))
    ]
    data = {
        "reviews": [review],
        "spans": spans,
        "relationships": relations,
        "fields": [
            {"case_id": case, "field": f, "status": "documented", "notes": ""}
            for f in workflow.FIELDS
        ],
    }
    write_review(directory, data)
    return data


def write_review(directory, data):
    for name, records in data.items():
        workflow.write_csv(directory / f"{name}.csv", workflow.CSV_COLUMNS[name], records)


def test_packet_is_blinded_escaped_and_exact(setup):
    corpus, packet, rows, manifest = setup
    cases = workflow.read_csv(packet / "reviewer/cases.csv", ["case_id", "text"])
    assert cases[0]["text"] == TEXT
    source = (packet / "reviewer/packet.html").read_text()
    assert "&lt;script&gt;" in source
    for path in (packet / "reviewer").iterdir():
        text = path.read_text()
        assert "SECRET" not in text
        assert "family-test" not in text
        assert rows["test"]["text_sha256"] not in text
    assert all(
        r["status"] == "pending"
        for r in workflow.read_csv(packet / "reviewer/fields.csv", workflow.CSV_COLUMNS["fields"])
    )
    with pytest.raises(ValueError, match="already exists"):
        workflow.packet(corpus, packet)


def test_valid_span_relationship_import_and_synthetic_provenance(setup, tmp_path):
    corpus, packet, rows, manifest = setup
    paths = [tmp_path / role for role in ("a", "b", "final")]
    for path in paths:
        review_at(path, manifest, path.name)
    imported = workflow.import_reviews(corpus, packet, *paths, tmp_path / "gold.json")
    assert imported["synthetic_only"] and not imported["clinical_validation"]
    case = imported["cases"][0]
    assert case["expected"]["ebus.short_axis_mm"] == ["7:8"]
    assert case["expected"]["ebus.observed_not_sampled"] == ["4L"]
    assert case["expected_relationships"]["localization.modality"] == ["RUL|radial_EBUS"]
    assert imported == workflow.import_reviews(corpus, packet, *paths, None)


@pytest.mark.parametrize(
    "mutation,match",
    [
        (lambda d: d["spans"][0].update(start="0"), "offset/text"),
        (lambda d: d["spans"][0].update(normalized="99"), "normalized"),
        (lambda d: d["spans"][1].update(normalized="NaN"), "finite"),
        (lambda d: d["spans"][1].update(text="8 mm", start=str(TEXT.index("8 mm"))), "short-axis"),
        (lambda d: d["spans"][2].update(normalized="3.5"), "integer"),
        (lambda d: d["spans"][3].update(assertion="negated"), "negated evidence"),
        (lambda d: d["relationships"][0].update(target_span_id="missing"), "Dangling"),
        (lambda d: d["relationships"][0].update(source_span_id="6"), "endpoint"),
        (
            lambda d: d["relationships"].append(
                dict(d["relationships"][0], relationship_id="other")
            ),
            "semantic",
        ),
        (lambda d: d["fields"][0].update(status="pending"), "Pending"),
        (lambda d: d["fields"].pop(), "all critical"),
        (lambda d: d["relationships"].pop(), "status"),
        (lambda d: d["reviews"][0].update(blinded="false"), "Blinding"),
        (lambda d: d["reviews"][0].update(completed_at="2026-10-10"), "timezone"),
        (lambda d: d["spans"][0].update(case_id="foreign-case"), "Unknown review"),
    ],
)
def test_rejects_invalid_review(setup, tmp_path, mutation, match):
    _, _, rows, manifest = setup
    path = tmp_path / "review"
    data = review_at(path, manifest)
    mutation(data)
    write_review(path, data)
    with pytest.raises(ValueError, match=match):
        workflow.load_review(path, rows, manifest)


def test_third_adjudicator_and_disagreement_required(setup, tmp_path):
    corpus, packet, rows, manifest = setup
    paths = [tmp_path / role for role in ("a", "b", "final")]
    for path in paths:
        review_at(path, manifest, "same-person")
    with pytest.raises(ValueError, match="distinct adjudicator"):
        workflow.import_reviews(corpus, packet, *paths, None)
    for path in paths:
        data = {
            name: workflow.read_csv(path / f"{name}.csv", cols)
            for name, cols in workflow.CSV_COLUMNS.items()
        }
        data["reviews"][0]["reviewer_id"] = path.name
        if path.name == "b":
            data["relationships"] = [
                r for r in data["relationships"] if r["field"] != "ebus.short_axis_mm"
            ]
            data["fields"][0].update(status="unknown", notes="Axis disputed")
        write_review(path, data)
    with pytest.raises(ValueError, match="resolution notes"):
        workflow.import_reviews(corpus, packet, *paths, None)


def test_scenario_audit_enforces_full_inventory_and_disjointness(setup):
    _, packet, rows, _ = setup
    path = packet / "coordinator/scenarios.csv"
    records = workflow.read_csv(path, workflow.SCENARIO_COLUMNS)
    assert not workflow.audit_scenarios(rows, path)["complete"]
    for row in records:
        row.update(status="reviewed", reviewer_id="scenario-reviewer")
    workflow.write_csv(path, workflow.SCENARIO_COLUMNS, records)
    assert workflow.audit_scenarios(rows, path)["complete"]
    records[0]["scenario_id"] = records[1]["scenario_id"]
    workflow.write_csv(path, workflow.SCENARIO_COLUMNS, records)
    with pytest.raises(ValueError, match="Scenario leakage"):
        workflow.audit_scenarios(rows, path)
    workflow.write_csv(path, workflow.SCENARIO_COLUMNS, records[:-1])
    with pytest.raises(ValueError, match="every corpus document"):
        workflow.audit_scenarios(rows, path)


def test_known_exposure_cannot_be_cleared(setup):
    _, packet, rows, _ = setup
    path = packet / "coordinator/scenarios.csv"
    records = workflow.read_csv(path, workflow.SCENARIO_COLUMNS)
    next(r for r in records if r["split"] == "train")["engineering_exposed"] = "false"
    workflow.write_csv(path, workflow.SCENARIO_COLUMNS, records)
    with pytest.raises(ValueError, match="cannot be cleared"):
        workflow.audit_scenarios(rows, path)


def test_source_and_frozen_artifact_tampering_fail(setup):
    corpus, packet, rows, manifest = setup
    (corpus / "test.jsonl").write_text("{}\n")
    with pytest.raises(ValueError, match="artifact changed"):
        workflow.load_corpus(corpus)


def test_positive_coverage_does_not_accept_absence_only_or_zero_support(setup, tmp_path):
    _, _, rows, manifest = setup
    path = tmp_path / "review"
    review_at(path, manifest)
    entry = next(iter(workflow.load_review(path, rows, manifest).values()))
    case = {**entry, "document_id": "test", "family_id": "family-test"}
    support = workflow.coverage([case])
    assert not support["all_required_positive_coverage"]
    assert support["safety_present"] == 0
    perfect = qualification.score([case], {"test": entry["expected"]}, "expected")
    assert qualification.targets_met(perfect)
    case["expected"]["ebus.short_axis_mm"] = []
    perfect = qualification.score([case], {"test": case["expected"]}, "expected")
    assert not qualification.targets_met(perfect)
    assert not workflow.coverage([case])["all_required_positive_coverage"]


def test_relation_scoring_detects_wrong_target():
    payload = {
        "proposal": {
            "targets": [
                {"target_id": "a", "site": "lung", "lobe": "RUL"},
                {"target_id": "b", "site": "lung", "lobe": "LLL"},
            ],
            "localization_events": [{"target_id": "b", "localization_modality": "radial_EBUS"}],
        }
    }
    actual = qualification.relationship_facts(payload)
    assert actual["localization.modality"] == {"LLL|radial_EBUS"}
    cases = [
        {
            "document_id": "test",
            "expected_relationships": {"localization.modality": ["RUL|radial_EBUS"]},
        }
    ]
    report = qualification.score(cases, {"test": actual}, "expected_relationships")
    assert report["metrics"]["localization.modality"]["false_positive"] == 1
    assert report["metrics"]["localization.modality"]["false_negative"] == 1


def test_readiness_blocks_without_inventing_reviews(setup, tmp_path):
    corpus, packet, _, _ = setup
    report = workflow.readiness(corpus, packet, tmp_path / "readiness.json")
    assert not report["promotion_allowed"]
    assert "clinical_adjudication_pending" in report["blocked_reasons"]
    assert "semantic_scenario_audit_pending" in report["blocked_reasons"]


def test_qualification_fails_closed_and_emits_report(setup, tmp_path):
    corpus, packet, _, _ = setup
    output = tmp_path / "failed.json"
    args = ["--corpus", str(corpus), "--packet", str(packet), "--output", str(output)]
    for flag in ("gold", "review-a", "review-b", "adjudication", "model-dir"):
        args.extend(["--" + flag, str(tmp_path / "missing")])
    assert qualification.main(args) == 2
    assert not json.loads(output.read_text())["promotion_allowed"]
    assert not (corpus / "independent_qualification_use.json").exists()


def test_family_and_cosmetic_scenario_overlap_rejected(setup):
    corpus, _, _, _ = setup
    path = corpus / "validation.jsonl"
    row = json.loads(path.read_text())
    row["family_id"] = "family-train"
    path.write_text(json.dumps(row) + "\n")
    manifest = json.loads((corpus / "split_manifest.json").read_text())
    manifest["artifacts"][path.name] = workflow.digest(path.read_bytes())
    workflow.save(corpus / "split_manifest.json", manifest)
    with pytest.raises(ValueError, match="Family assignment"):
        workflow.load_corpus(corpus)
    row["family_id"] = "family-validation"
    row["text"] = json.loads((corpus / "train.jsonl").read_text())["text"]
    row["text_sha256"] = workflow.digest(row["text"])
    path.write_text(json.dumps(row) + "\n")
    manifest["artifacts"][path.name] = workflow.digest(path.read_bytes())
    workflow.save(corpus / "split_manifest.json", manifest)
    with pytest.raises(ValueError, match="crosses splits"):
        workflow.load_corpus(corpus)


def test_imported_gold_cannot_be_edited_after_review(setup, tmp_path):
    corpus, packet, rows, manifest = setup
    paths = [tmp_path / role for role in ("a", "b", "final")]
    for path in paths:
        review_at(path, manifest, path.name)
    gold_path = tmp_path / "gold.json"
    gold = workflow.import_reviews(corpus, packet, *paths, gold_path)
    gold["cases"][0]["expected"]["ebus.short_axis_mm"] = ["7:99"]
    workflow.save(gold_path, gold)
    with pytest.raises(ValueError, match="differs from validated"):
        qualification.qualification(
            corpus, packet, gold_path, *paths, tmp_path / "model", tmp_path / "result.json"
        )


@pytest.mark.parametrize("degraded", [False, True])
def test_qualification_measures_independent_evidence_but_never_clinical_release(
    tmp_path, monkeypatch, degraded
):
    """Fake runtime isolates gate behavior; review parsing is tested with real CSVs above."""
    import sys
    from types import SimpleNamespace

    from ip_registry_engine import engine

    from ops.tools import eval_robotic_ebus as evaluation

    corpus = tmp_path / "corpus"
    corpus.mkdir()
    model_dir = tmp_path / "model"
    model_dir.mkdir()
    workflow.save(
        model_dir / "focused-model-manifest.json",
        {
            "corpus_manifest_sha256": "frozen",
            "training_split": "train",
            "selection_split": "validation",
            "heldout_split": "test",
        },
    )
    expected = {field: ["value"] for field in workflow.FIELDS}
    cases = []
    for key, safety in (("one", "present"), ("two", "absent")):
        facts = {**expected, "safety.immediate": [safety]}
        cases.append(
            {
                "document_id": key,
                "family_id": key,
                "reviews": [{"independent": "true"}],
                "fields": {f: {"status": "documented"} for f in workflow.FIELDS},
                "expected": facts,
                "expected_relationships": facts,
            }
        )
    gold = {"cases": cases}
    gold_path = tmp_path / "gold.json"
    workflow.save(gold_path, gold)
    rows = {
        c["document_id"]: {
            "document_id": c["document_id"],
            "text": c["document_id"],
            "text_sha256": workflow.digest(c["document_id"]),
        }
        for c in cases
    }
    monkeypatch.setattr(
        qualification, "load_packet", lambda *_: (rows, {"corpus_manifest_sha256": "frozen"})
    )
    monkeypatch.setattr(
        qualification,
        "audit_scenarios",
        lambda *_: {
            "complete": True,
            "documents": {key: {"scenario_id": key} for key in rows},
            "exposed_scenarios": [],
            "sha256": "audit",
        },
    )
    monkeypatch.setattr(qualification, "import_reviews", lambda *_: gold)
    monkeypatch.setattr(qualification, "model_identity", lambda *_: "model-hash")
    by_text = {c["document_id"]: c["expected"] for c in cases}

    class Provider:
        ner = object()

        def __init__(self, *_):
            pass

        def extract(self, request):
            return SimpleNamespace(
                status="degraded" if degraded else "proposed",
                observations={
                    "facts": by_text[request.text],
                    "inference": {
                        "ner_available": not degraded,
                        "model_manifest_digest": "model-hash",
                    },
                },
            )

    class Baseline:
        parallel_orchestrator = SimpleNamespace(ner_predictor=SimpleNamespace(available=True))
        _registry_ml_predictor = SimpleNamespace(available=True)

        def extract_fields_extraction_first(self, text):
            return SimpleNamespace(registry=SimpleNamespace(model_dump=lambda: by_text[text]))

    monkeypatch.setattr(engine, "LocalDeterministicProvider", Provider)
    monkeypatch.setitem(
        sys.modules,
        "app.registry.application.registry_service",
        SimpleNamespace(RegistryService=Baseline),
    )
    monkeypatch.setattr(evaluation, "focused_facts", lambda payload: payload["facts"])
    monkeypatch.setattr(evaluation, "baseline_facts", lambda payload: payload)
    monkeypatch.setattr(qualification, "relationship_facts", lambda payload: payload["facts"])
    result = qualification.qualification(
        corpus,
        tmp_path,
        gold_path,
        tmp_path,
        tmp_path,
        tmp_path,
        model_dir,
        tmp_path / "result.json",
    )
    assert result["independent_synthetic_qualification_passed"] is (not degraded)
    assert result["promotion_allowed"] is False
    assert result["clinical_validation"] is False
    assert (corpus / "independent_qualification_use.json").exists()
    with pytest.raises(ValueError, match="already exposed"):
        qualification.qualification(
            corpus,
            tmp_path,
            gold_path,
            tmp_path,
            tmp_path,
            tmp_path,
            model_dir,
            tmp_path / "second-result.json",
        )


def test_canonical_exposure_propagates_to_entire_family(setup, tmp_path, monkeypatch):
    _, packet, rows, _ = setup
    pilot = tmp_path / "reviewed_eval_selection.json"
    workflow.save(pilot, {"cases": []})
    workflow.save(
        tmp_path / "qualification_exposure.json",
        {
            "events": [{"document_ids": ["test"]}],
        },
    )
    monkeypatch.setattr(workflow, "DEFAULT_EXPOSED", pilot)
    assert "family-test" in workflow.known_exposed(rows)
    with pytest.raises(ValueError, match="Known exposure cannot be cleared"):
        workflow.audit_scenarios(rows, packet / "coordinator/scenarios.csv")


def test_modified_html_source_cannot_be_imported(setup):
    corpus, packet, _, _ = setup
    path = packet / "reviewer/packet.html"
    path.write_text(path.read_text().replace("8 mm", "9 mm"))
    with pytest.raises(ValueError, match="HTML changed"):
        workflow.load_packet(corpus, packet)
