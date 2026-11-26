from __future__ import annotations

import os
import re
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_coding_service, get_registry_service
from app.api.fastapi_app import app
from app.api.phi_dependencies import get_phi_scrubber
from app.api.readiness import require_ready

os.environ.setdefault("PROCSUITE_SKIP_WARMUP", "1")


@pytest.fixture
def client():
    return TestClient(app)


def test_phi_redactor_index_has_coop_coep_headers(client: TestClient) -> None:
    resp = client.get("/ui/phi_redactor/")
    assert resp.status_code == 200
    assert resp.headers.get("Cross-Origin-Opener-Policy") == "same-origin"
    assert resp.headers.get("Cross-Origin-Embedder-Policy") == "require-corp"


def test_phi_redactor_redirects_trailing_slash(client: TestClient) -> None:
    resp = client.get("/ui/phi_redactor", follow_redirects=False)
    assert resp.status_code in (301, 302, 303, 307, 308)
    assert resp.headers.get("location") == "/ui/phi_redactor/"
    # Even the redirect response should carry headers for debugging/consistency.
    assert resp.headers.get("Cross-Origin-Opener-Policy") == "same-origin"
    assert resp.headers.get("Cross-Origin-Embedder-Policy") == "require-corp"


def test_phi_redactor_assets_have_coop_coep_headers(client: TestClient) -> None:
    """Test that all PHI redactor static assets have COOP/COEP headers."""
    for path in (
        "/ui/phi_redactor/index.html",
        "/ui/reporter_builder.html",
        "/ui/reporter_builder.js",
        "/ui/speech.worker.js",
        "/ui/speechTranscriptRepair.js",
        "/ui/phi_redactor/app.js",
        "/ui/phi_redactor/redactor.worker.js",
        "/ui/phi_redactor/styles.css",
        "/ui/phi_redactor/allowlist_trie.json",
        "/ui/phi_redactor/sw.js",
        # Embedded RegistryGrid assets (served under /ui/* to preserve COOP/COEP)
        "/ui/registry_grid/registry_grid.iife.js",
        "/ui/registry_grid/registry_grid.css",
    ):
        resp = client.get(path)
        assert resp.status_code == 200, path
        assert resp.headers.get("Cross-Origin-Opener-Policy") == "same-origin", (
            f"Missing COOP header for {path}"
        )
        assert resp.headers.get("Cross-Origin-Embedder-Policy") == "require-corp", (
            f"Missing COEP header for {path}"
        )


def test_reporter_builder_subpage_is_linked_from_topbar(client: TestClient) -> None:
    index_resp = client.get("/ui/")
    assert index_resp.status_code == 200
    assert 'href="./reporter_builder.html"' in index_resp.text

    workflow_resp = client.get("/ui/workflow.html")
    assert workflow_resp.status_code == 200
    assert 'href="./reporter_builder.html"' in workflow_resp.text


def test_reporter_builder_can_transfer_note_to_dashboard(client: TestClient) -> None:
    reporter_html = client.get("/ui/reporter_builder.html")
    assert reporter_html.status_code == 200
    assert 'id="transferToDashboardBtn"' in reporter_html.text

    reporter_js = client.get("/ui/reporter_builder.js")
    assert reporter_js.status_code == 200
    assert "ps.reporter_to_dashboard_note_v1" in reporter_js.text

    dashboard_js = client.get("/ui/phi_redactor/app.js")
    assert dashboard_js.status_code == 200
    assert "consumeReporterTransferPayload" in dashboard_js.text
    assert "ps.reporter_to_dashboard_note_v1" in dashboard_js.text


def test_reporter_builder_has_speech_dictation_controls_and_same_origin_worker(
    client: TestClient,
) -> None:
    reporter_html = client.get("/ui/reporter_builder.html")
    assert reporter_html.status_code == 200
    html = reporter_html.text
    assert 'id="speechStartConfirmModal"' in html
    assert 'id="speechStartConfirmBtn"' in html
    assert 'id="speechStartCancelBtn"' in html
    assert 'id="speechStartBtn"' in html
    assert 'id="speechStopBtn"' in html
    assert 'id="speechDiscardBtn"' in html
    assert 'id="speechCloudFallbackBtn"' in html
    assert 'id="speechModelSelect"' not in html
    assert 'id="speechModelHintText"' not in html
    assert 'id="speechCleanBtn"' not in html
    assert "Do not speak patient names, MRN, DOB, phone, address, or exact dates." in html
    assert "Confirm and Start Dictation" in html
    assert (
        "I confirm that I will not include patient names, MRN, DOB, phone, address, "
        "or exact dates in this dictation."
    ) in html
    assert "Cloud transcription runs by default after you stop" in html
    assert "Use Local Tiny Fallback" in html
    assert "uploaded to the configured cloud transcription provider after I stop recording" in html

    reporter_js = client.get("/ui/reporter_builder.js")
    assert reporter_js.status_code == 200
    js = reporter_js.text
    assert '"/report/transcribe_audio"' in js
    assert '"/report/clean_seed_text"' in js
    assert "cloud_fallback_confirmed" in js
    assert "speechStartConfirmModal" in js
    assert "speechStartConfirmedForCurrentNote" in js
    assert "http://localhost:8000 or http://127.0.0.1:8000 instead of http://0.0.0.0:8000" in js
    assert "Waiting for microphone permission" in js
    assert "Allow microphone access for localhost in Chrome and macOS System Settings" in js
    assert "Auto-cleaning scrubbed transcript" in js
    assert "Transcript auto-cleaned after redaction. Confirm PHI removal, then seed." in js
    assert 'const REPORTER_SPEECH_DEFAULT_MODEL_KEY = "tiny"' in js
    assert "Cloud transcription ready. Record a short non-PHI dictation." in js
    assert "Cloud transcription failed. Trying local Tiny fallback" in js
    assert "Cloud transcription was unavailable, so local Tiny fallback was used." in js
    assert "transcription timed out after" in js

    worker_js = client.get("/ui/speech.worker.js")
    assert worker_js.status_code == 200
    worker_body = worker_js.text
    assert 'from "./transformers.min.js"' in worker_body
    assert "wasmPaths = ONNX_WASM_BASE_URL" in worker_body
    assert 'bundleId: "speech_whisper_base_en"' in worker_body
    assert 'bundleId: "speech_whisper_tiny_en"' in worker_body
    assert 'const DEFAULT_MODEL_KEY = "tiny"' in worker_body
    assert 'type: "status"' in worker_body
    assert "cdn.jsdelivr" not in worker_body

    repair_js = client.get("/ui/speechTranscriptRepair.js")
    assert repair_js.status_code == 200
    repair_body = repair_js.text
    assert "station_with_side" in repair_body
    assert '"lidocaine"' in repair_body


def test_phi_redactor_index_has_formatted_report_sections(client: TestClient) -> None:
    resp = client.get("/ui/phi_redactor/index.html")
    assert resp.status_code == 200
    assert 'id="billingSelectedBody"' in resp.text
    assert 'id="evidenceTraceabilityHost"' in resp.text
    assert 'id="registryGridRoot"' in resp.text
    assert 'id="correctOcrBtn"' in resp.text
    assert 'id="exportEditedBtn"' in resp.text
    assert 'id="exportPatchBtn"' in resp.text


def test_registry_grid_bundle_exports_global_api(client: TestClient) -> None:
    resp = client.get("/ui/registry_grid/registry_grid.iife.js")
    assert resp.status_code == 200
    body = resp.text
    assert "window.RegistryGrid" in body
    # Minimal contract: mount/update/unmount should exist
    # (string check is enough for smoke coverage).
    assert "mount" in body
    assert "update" in body
    assert "unmount" in body


def test_phi_redactor_worker_stoplist_includes_lymph_nodes(client: TestClient) -> None:
    """Regression: don't treat "Lymph Nodes" headings as patient names."""
    resp = client.get("/ui/phi_redactor/redactor.worker.js")
    assert resp.status_code == 200
    body = resp.text
    assert re.search(
        r"const\s+NAME_REGEX_CLINICAL_STOPLIST\s*=\s*new\s+Set\(\[[\s\S]*?\"lymph\"[\s\S]*?\"node\"[\s\S]*?\"nodes\"",
        body,
        re.MULTILINE,
    ), "Expected lymph/node/nodes in NAME_REGEX_CLINICAL_STOPLIST"


def test_phi_redactor_worker_gates_procedure_for_clinical_phrases(client: TestClient) -> None:
    """Regression: don't flag 'EBUS for peripheral lesion' as a patient name."""
    resp = client.get("/ui/phi_redactor/redactor.worker.js")
    assert resp.status_code == 200
    body = resp.text
    assert re.search(
        r"for\s*\(const\s+match\s+of\s+text\.matchAll\(PROCEDURE_FOR_NAME_RE\)\)\s*\{[\s\S]*?isInClinicalStoplist\(firstName\)[\s\S]*?continue;",
        body,
        re.MULTILINE,
    ), "Expected clinical stoplist gating inside PROCEDURE_FOR_NAME_RE loop"


def test_phi_redactor_legacy_worker_has_same_regression_fixes(client: TestClient) -> None:
    resp = client.get("/ui/redactor.worker.legacy.js")
    assert resp.status_code == 200
    body = resp.text
    assert re.search(
        r"const\s+NAME_REGEX_CLINICAL_STOPLIST\s*=\s*new\s+Set\(\[[\s\S]*?\"lymph\"[\s\S]*?\"node\"[\s\S]*?\"nodes\"",
        body,
        re.MULTILINE,
    ), "Expected lymph/node/nodes in legacy NAME_REGEX_CLINICAL_STOPLIST"
    assert re.search(
        r"for\s*\(const\s+match\s+of\s+text\.matchAll\(PROCEDURE_FOR_NAME_RE\)\)\s*\{[\s\S]*?isInClinicalStoplist\(firstName\)[\s\S]*?continue;",
        body,
        re.MULTILINE,
    ), "Expected clinical stoplist gating inside legacy PROCEDURE_FOR_NAME_RE loop"


_REDACTOR_WORKERS = [
    f"{folder}/{name}"
    for folder in ("phi_redactor", "phi_redactor_classic")
    for name in ("redactor.worker.js", "redactor.worker.legacy.js")
]


def _first_name_detector(worker: str):
    """The standalone-first-name rule as a worker file defines it: regex, stoplist, suffix gate."""
    body = (Path(__file__).resolve().parents[2] / "ui" / "static" / worker).read_text()
    name_re = re.search(r"const FIRST_NAME_CLINICAL_RE =\s*/(.+)/g;", body).group(1)
    stoplist = set(
        re.findall(
            r'"([^"]+)"',
            re.search(
                r"const SINGLE_NAME_CLINICAL_STOPLIST = new Set\(\[([\s\S]*?)\]\);", body
            ).group(1),
        )
    )
    suffix_re = re.search(r"const CLINICAL_TERM_SUFFIX_RE =\s*/(.+)/i;", body).group(1)
    assert re.search(
        r"matchAll\(FIRST_NAME_CLINICAL_RE\)\)\s*\{[\s\S]*?"
        r"SINGLE_NAME_CLINICAL_STOPLIST\.has\(nameGroup\.toLowerCase\(\)\)\s*\|\|\s*"
        r"CLINICAL_TERM_SUFFIX_RE\.test\(nameGroup\)\)\s*\{\s*continue;",
        body,
    ), "Expected the stoplist and suffix gate inside the FIRST_NAME_CLINICAL_RE loop"

    def flagged(text: str) -> list[str]:
        return [
            m.group(1)
            for m in re.finditer(name_re, text)
            if m.group(1).lower() not in stoplist
            and not re.search(suffix_re, m.group(1), re.IGNORECASE)
        ]

    return flagged


@pytest.mark.parametrize("worker", _REDACTOR_WORKERS)
@pytest.mark.parametrize(
    "sentence",
    [
        "Fluoroscopy was used during sampling.",
        "Mediastinoscopy was not performed.",
        "Elastography was performed at each station.",
        "Thoracotomy was avoided.",
        "Tracheomalacia was noted as we advanced the scope.",
        "Adequacy was confirmed after the third pass.",
        "Localization was corroborated with radial EBUS.",
        "Placement was confirmed via ultrasound.",
        "Fluid was evacuated.",
        "Flumazenil was administered with immediate effect.",
    ],
)
def test_phi_redactor_first_name_rule_skips_sentence_initial_clinical_nouns(
    worker: str, sentence: str
) -> None:
    """Suppress: "Fluoroscopy was used ..." must not be read as a first name plus a verb."""
    assert _first_name_detector(worker)(f"The lesion was reached. {sentence}") == []


@pytest.mark.parametrize("worker", _REDACTOR_WORKERS)
@pytest.mark.parametrize(
    ("sentence", "name"),
    [
        ("Frank underwent a procedure.", "Frank"),
        ("HPI: Susan is a 71-year-old female here for cough.", "Susan"),
        ("Ms. Chen is a 72-year-old female with a lung mass.", "Chen"),
        ("Mr. White has a very early stage cancer.", "White"),
        ("Mr. Fields has a tumor blocking his right mainstem.", "Fields"),
    ],
)
def test_phi_redactor_first_name_rule_still_flags_names(
    worker: str, sentence: str, name: str
) -> None:
    """Preserve: real names in front of the same verbs are still proposed for redaction."""
    assert _first_name_detector(worker)(sentence) == [name]


@pytest.mark.parametrize("folder", ["phi_redactor", "phi_redactor_classic"])
def test_phi_redactor_legacy_veto_is_the_module_veto(folder: str) -> None:
    """The fallback worker's veto file is the module file minus ``export``, plus a global.

    It had fallen behind once (no guideline-citation rule, four platform names missing), so
    browsers on the fallback redacted text the main redactor keeps. Regenerate it from
    protectedVeto.js with exactly these three edits whenever that file changes.
    """
    static = Path(__file__).resolve().parents[2] / "ui" / "static"
    module = (static / "phi_redactor" / "protectedVeto.js").read_text()
    assert (static / folder / "protectedVeto.js").read_text() == module
    assert module.count("// Main export\n") == 1
    assert module.count("\nexport function applyVeto(") == 1
    expected = (
        module.replace("// Main export\n", "// Main export (legacy worker attaches to self)\n")
        .replace("\nexport function applyVeto(", "\nfunction applyVeto(")
        .rstrip("\n")
        + "\n\nself.applyVeto = applyVeto;\n"
    )
    assert (static / folder / "protectedVeto.legacy.js").read_text() == expected


_VETO_RUNNER = """
const fs = require("fs");
const vm = require("vm");
const [vetoPath, termsPath] = process.argv.slice(1);
const ctx = { self: {}, console: { log() {} } };
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(vetoPath, "utf8"), ctx);
const terms = JSON.parse(fs.readFileSync(termsPath, "utf8"));
const cases = JSON.parse(fs.readFileSync(0, "utf8"));
const out = cases.map(([text, word]) => {
  const start = text.indexOf(word);
  const span = { start, end: start + word.length, label: "PATIENT", score: 0.95 };
  return ctx.self.applyVeto([span], text, terms, { protectProviders: false }).length === 1;
});
process.stdout.write(JSON.stringify(out));
"""


def _still_redacted(cases: list[tuple[str, str]]) -> list[bool]:
    """Run the fallback veto file (tested equal to the module one) on PATIENT spans in node."""
    import json
    import shutil
    import subprocess

    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed")
    redactor = Path(__file__).resolve().parents[2] / "ui" / "static" / "phi_redactor"
    result = subprocess.run(
        [
            node,
            "-e",
            _VETO_RUNNER,
            str(redactor / "protectedVeto.legacy.js"),
            str(redactor / "vendor" / "phi_distilbert_ner" / "protected_terms.json"),
        ],
        input=json.dumps(cases),
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    )
    return json.loads(result.stdout)


def test_phi_veto_citation_rule_does_not_release_patient_names() -> None:
    """Preserve: a year, "chest" or "recommendations" near a name is not a citation.

    The rule used to treat any of those within 90 characters as citation context, so the
    veto dropped the patient-name detection in ordinary note headers.
    """
    cases = [
        (
            "Patient: John Smith\nDOB: 01/15/1960\nIndication: abnormal chest CT with a nodule.",
            "John Smith",
        ),
        ("NAME: DARRELL BROOKS: 5/16/1964 DOD#: 51113915741\nIMPRESSION: Mediastinal", "DARRELL"),
        ("Mr. Smith was seen 3/2/2025 after a chest radiograph showed an effusion.", "Smith"),
        ("Maria Lopez underwent EBUS on 2026-01-04. Recommendations: clinic.", "Maria Lopez"),
        ("John Smith was referred in 2025 by the tumor board committee.", "John Smith"),
    ]
    assert _still_redacted(cases) == [True] * len(cases)


def test_phi_veto_citation_rule_still_keeps_cited_authors_and_societies() -> None:
    """Suppress: the span that is itself the citation stays visible."""
    cases = [
        ("Nodule follow-up per MacMahon et al, 2017 (Fleischner Society).", "MacMahon"),
        ("Managed per MacMahon H, et al. Radiology 2017.", "MacMahon"),
        ("Follow-up per Fleischner Society recommendations.", "Fleischner"),
        ("Follow-up per Fleischner Society recommendations.", "Fleischner Society"),
        ("Staging followed the CHEST guideline.", "CHEST"),
    ]
    assert _still_redacted(cases) == [False] * len(cases)


def test_phi_veto_citation_rule_reads_the_span_not_its_surroundings() -> None:
    """Always-on guard (no node needed) against the two constructs that caused the leak."""
    body = (
        Path(__file__).resolve().parents[2] / "ui" / "static" / "phi_redactor" / "protectedVeto.js"
    ).read_text()
    rule = body[
        body.index("function isGuidelineCitation(") : body.index("function isProviderName(")
    ]
    assert "getContext(" not in rule
    assert "CITATION_YEAR_RE" not in body


def test_phi_redactor_worker_provider_roles_cover_ebus_headers(client: TestClient) -> None:
    """Regression: provider role regex should include common EBUS header labels."""
    resp = client.get("/ui/phi_redactor/redactor.worker.js")
    assert resp.status_code == 200
    body = resp.text
    assert "const PROVIDER_ROLE_LINE_RE" in body
    assert "Endoscopist" in body
    assert "Fellow\\/Resident" in body
    assert "Technician" in body
    assert "Additional\\s+Fellow" in body
    assert "Additional\\s+Technician" in body
    assert 'source: "regex_provider_role"' in body


def test_phi_redactor_worker_has_address_and_zip_regex_detectors(client: TestClient) -> None:
    """Regression: street address + ZIP context should be captured by deterministic regex."""
    resp = client.get("/ui/phi_redactor/redactor.worker.js")
    assert resp.status_code == 200
    body = resp.text
    assert "const STREET_ADDRESS_RE" in body
    assert "const CITY_STATE_ZIP_RE" in body
    assert "const ZIP_LABEL_RE" in body
    assert "text.matchAll(STREET_ADDRESS_RE)" in body
    assert "text.matchAll(CITY_STATE_ZIP_RE)" in body
    assert "text.matchAll(ZIP_LABEL_RE)" in body
    assert 'source: "regex_address"' in body
    assert 'source: "regex_city_state_zip"' in body
    assert 'source: "regex_zip_label"' in body


def test_phi_redactor_legacy_worker_has_address_and_provider_role_detectors(
    client: TestClient,
) -> None:
    """Legacy worker fallback should keep parity for address + provider role coverage."""
    resp = client.get("/ui/redactor.worker.legacy.js")
    assert resp.status_code == 200
    body = resp.text
    assert "const PROVIDER_ROLE_LINE_RE" in body
    assert "Endoscopist" in body
    assert "Fellow\\/Resident" in body
    assert "Technician" in body
    assert "const STREET_ADDRESS_RE" in body
    assert "const CITY_STATE_ZIP_RE" in body
    assert "const ZIP_LABEL_RE" in body
    assert 'source: "regex_provider_role"' in body
    assert 'source: "regex_address"' in body


def test_unified_process_already_scrubbed_bypasses_server_scrubber(
    monkeypatch, client: TestClient
) -> None:
    class StubRegistryService:
        def __init__(self) -> None:
            self.seen_note: str | None = None

        def extract_fields(self, note_text: str):
            self.seen_note = note_text
            record = SimpleNamespace(model_dump=lambda **_: {})
            return SimpleNamespace(
                record=record,
                cpt_codes=[],
                coder_difficulty="HIGH_CONF",
                coder_source="stub",
                mapped_fields={},
                derivation_warnings=[],
                warnings=[],
                needs_manual_review=False,
                validation_errors=[],
                audit_warnings=[],
            )

    class StubKBRepo:
        version = "test_kb"

        def get_procedure_info(self, _code: str):
            return None

    class StubCodingService:
        kb_repo = StubKBRepo()

    stub_registry = StubRegistryService()

    # Hard-fail if the server-side scrubbing helper is invoked.
    from app.api.services import unified_pipeline as unified_pipeline_module

    def _fail_apply(*_args, **_kwargs):
        raise AssertionError("apply_phi_redaction should not be called when already_scrubbed=true")

    monkeypatch.setattr(unified_pipeline_module, "apply_phi_redaction", _fail_apply)

    async def _run_cpu_direct(_app, fn, *args):  # noqa: ANN001
        return fn(*args)

    monkeypatch.setattr(unified_pipeline_module, "run_cpu", _run_cpu_direct)

    # Avoid unrelated readiness dependencies
    app.dependency_overrides[require_ready] = lambda: None
    app.dependency_overrides[get_registry_service] = lambda: stub_registry
    app.dependency_overrides[get_coding_service] = lambda: StubCodingService()
    app.dependency_overrides[get_phi_scrubber] = lambda: (lambda text: text)

    try:
        note = "RAW_TEXT_SHOULD_PASS_THROUGH_UNCHANGED"
        resp = client.post(
            "/api/v1/process",
            json={"note": note, "already_scrubbed": True, "include_financials": False},
        )
        assert resp.status_code == 200
        assert stub_registry.seen_note == note
    finally:
        app.dependency_overrides.clear()


def test_phi_veto_header_device_and_patient_rules_do_not_release_patient_names() -> None:
    """Preserve: a name in a patient position survives the header, device and verb rules.

    Each of these was dropped before: a name right after "Indication:" or "IMPRESSION/PLAN:",
    a surname that is also a manufacturer (Baker, Cook, King, Wang, Young), and a name after
    the word "patient" that happens to end like a verb (Thomas, James, Helen, Karen).
    """
    cases = [
        ("INDICATION: John Smith is a 65-year-old male with a nodule.", "John Smith"),
        ("Indication: Helen Carter, a 70 year old female with a mass.", "Helen Carter"),
        ("IMPRESSION/PLAN: Nira Kaplan is a 85 year old female who presents", "Nira Kaplan"),
        ("IMPRESSION/PLAN: Elizabeth Larkin is a 89 year old female", "Elizabeth"),
        ("Indication: Mary Jones underwent prior lobectomy.", "Mary Jones"),
        ("Diagnosis: Mr. Young has stage IIIA adenocarcinoma.", "Mr. Young"),
        ("Diagnosis: Mr. Young has stage IIIA adenocarcinoma.", "Young"),
        ("OPERATIVE NARRATIVE: Mr. Baker presented with an obstruction.", "Baker"),
        ("Mrs. Cook had a 13mm nodule in the left lower lobe.", "Cook"),
        ("Patient name: Young, Lori\nMRN: 3419905", "Young"),
        ("Patient: King, Melissa (F)\nMRN: 4420791", "King"),
        ("Name: Wang, Li\nDate of procedure: today", "Wang"),
        ("The requisition lists patient Thomas Cruz with MRN 5395351.", "Thomas Cruz"),
        ("The requisition lists patient Thomas Cruz with MRN 5395351.", "Thomas"),
        ("Patient James was intubated with a size 8.0 ETT.", "James"),
        ("The patient Helen was brought to the suite.", "Helen"),
        ("The form names patient Will Smith as the signer.", "Will Smith"),
    ]
    assert _still_redacted(cases) == [True] * len(cases)


def test_phi_veto_header_device_and_patient_rules_still_release_clinical_text() -> None:
    """Suppress: the same three rules keep clinical values, devices and verbs visible."""
    cases = [
        ("Procedure: Bronchoscopy with EBUS-TBNA", "Bronchoscopy"),
        ("Procedure Name: Thoracoscopy with pleural biopsy", "Thoracoscopy"),
        ("Indication: Mediastinal adenopathy", "Mediastinal adenopathy"),
        ("Indication: Lung Nodule\n65 year old male with a nodule.", "Lung Nodule"),
        ("Findings: Granuloma is a likely cause of the 3 cm lesion.", "Granuloma"),
        ("A Cook stent was not placed.", "Cook"),
        ("The Wang needle was used for three passes.", "Wang"),
        ("An Olympus scope and a Young retractor were available.", "Young"),
        ("Patient tolerated the procedure well.", "tolerated"),
        ("The patient remains intubated.", "remains"),
        ("PATIENT DENIES chest pain.", "DENIES"),
        ("Patient Status at Conclusion: stable", "Status"),
        ("PATIENT DEMOGRAPHICS:\nAge: 71", "DEMOGRAPHICS"),
    ]
    assert _still_redacted(cases) == [False] * len(cases)


def _patient_word_name_detector(worker: str):
    """The "patient First Last" rule as a worker file defines it."""
    body = (Path(__file__).resolve().parents[2] / "ui" / "static" / worker).read_text()
    name_re = re.search(r"const PATIENT_WORD_NAME_RE =\s*/(.+)/g;", body).group(1)
    assert "matchAll(PATIENT_WORD_NAME_RE)" in body
    assert 'source: "regex_patient_word_name"' in body
    return lambda text: [m.group(1) for m in re.finditer(name_re, text)]


@pytest.mark.parametrize("worker", _REDACTOR_WORKERS)
def test_phi_redactor_flags_a_full_name_after_the_word_patient(worker: str) -> None:
    """Preserve: "... lists patient Michael Baker with MRN" had no detection at all."""
    flagged = _patient_word_name_detector(worker)
    assert flagged("The requisition lists patient Michael Baker with MRN=2311352.") == [
        "Michael Baker"
    ]
    assert flagged("The patient Stephen Reyes was brought to the suite.") == ["Stephen Reyes"]
    assert flagged("Consent was signed by patient Mary A. O'Brien today.") == ["Mary A. O'Brien"]


@pytest.mark.parametrize("worker", _REDACTOR_WORKERS)
@pytest.mark.parametrize(
    "sentence",
    [
        "The patient tolerated the procedure well.",
        "The patient was brought to the Bronchoscopy suite.",
        "With the patient Supine, the scope was advanced.",
        "Patient Status at Conclusion: stable.",
        "The patient\nThomas Cruz was the proceduralist.",
    ],
)
def test_phi_redactor_patient_word_rule_needs_two_capitalised_words(
    worker: str, sentence: str
) -> None:
    """Suppress: a verb, one capitalised word, a heading or a line break never matches."""
    assert _patient_word_name_detector(worker)(sentence) == []
