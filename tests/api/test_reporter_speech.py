from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from app.api.routes import reporting as reporting_module
from app.reporting.speech_support import (
    ReporterSpeechCleanupResult,
    ReporterSpeechTranscriptionResult,
)

_REPAIR_MODULE = (
    Path(__file__).resolve().parents[2]
    / "ui"
    / "static"
    / "phi_redactor"
    / "speechTranscriptRepair.js"
)


@pytest.mark.asyncio
async def test_report_transcribe_audio_success(api_client, monkeypatch) -> None:
    async def _fake_transcribe(**_kwargs):
        return ReporterSpeechTranscriptionResult(
            transcript="EBUS TBNA at station 7",
            provider="openai",
            model="gpt-4o-mini-transcribe",
            fallback_used=True,
            warnings=["REPORTER_SPEECH_FALLBACK_USED"],
        )

    monkeypatch.setattr(reporting_module, "transcribe_reporter_audio", _fake_transcribe)

    response = await api_client.post(
        "/report/transcribe_audio",
        data={"source": "reporter_builder", "cloud_fallback_confirmed": "true"},
        files={"audio_file": ("dictation.webm", b"fake-audio", "audio/webm")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["transcript"] == "EBUS TBNA at station 7"
    assert payload["provider"] == "openai"
    assert payload["model"] == "gpt-4o-mini-transcribe"
    assert payload["fallback_used"] is True
    assert payload["warnings"] == ["REPORTER_SPEECH_FALLBACK_USED"]


@pytest.mark.asyncio
async def test_report_transcribe_audio_disabled_returns_503(api_client, monkeypatch) -> None:
    monkeypatch.setenv("REPORTER_SPEECH_ENABLED", "0")

    response = await api_client.post(
        "/report/transcribe_audio",
        data={"source": "reporter_builder", "cloud_fallback_confirmed": "true"},
        files={"audio_file": ("dictation.webm", b"fake-audio", "audio/webm")},
    )

    assert response.status_code == 503
    assert "disabled" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_report_transcribe_audio_offline_returns_503(api_client, monkeypatch) -> None:
    monkeypatch.setenv("REPORTER_SPEECH_ENABLED", "1")
    monkeypatch.setenv("REPORTER_SPEECH_ALLOW_CLOUD_FALLBACK", "1")
    monkeypatch.setenv("LLM_PROVIDER", "openai_compat")
    monkeypatch.setenv("OPENAI_OFFLINE", "1")

    response = await api_client.post(
        "/report/transcribe_audio",
        data={"source": "reporter_builder", "cloud_fallback_confirmed": "true"},
        files={"audio_file": ("dictation.webm", b"fake-audio", "audio/webm")},
    )

    assert response.status_code == 503
    assert "offline" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_report_clean_seed_text_requires_already_scrubbed(api_client) -> None:
    response = await api_client.post(
        "/report/clean_seed_text",
        json={
            "text": "EBUS TBNA at station 7",
            "already_scrubbed": False,
            "source": "speech_local",
            "strict": True,
        },
    )

    assert response.status_code == 422
    assert "already_scrubbed" in response.json()["detail"]


@pytest.mark.asyncio
async def test_report_clean_seed_text_strict_rejects_phi(api_client) -> None:
    response = await api_client.post(
        "/report/clean_seed_text",
        json={
            "text": "Patient: John Doe DOB: 01/01/1980",
            "already_scrubbed": True,
            "source": "speech_local",
            "strict": True,
        },
    )

    assert response.status_code == 422
    assert "phi" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_report_clean_seed_text_success(api_client, monkeypatch) -> None:
    def _fake_clean(_text: str, *, already_scrubbed: bool, strict: bool):
        assert already_scrubbed is True
        assert strict is True
        return ReporterSpeechCleanupResult(
            cleaned_text="EBUS TBNA at station 4R",
            changed=True,
            correction_applied=True,
            model="gpt-5.4-mini",
            warnings=["REPORTER_SPEECH_CLEANED"],
        )

    monkeypatch.setattr(reporting_module, "clean_scrubbed_reporter_transcript", _fake_clean)

    response = await api_client.post(
        "/report/clean_seed_text",
        json={
            "text": "e bus tbna at station four are",
            "already_scrubbed": True,
            "source": "speech_local",
            "strict": True,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["cleaned_text"] == "EBUS TBNA at station 4R"
    assert payload["changed"] is True
    assert payload["correction_applied"] is True
    assert payload["model"] == "gpt-5.4-mini"
    assert payload["warnings"] == ["REPORTER_SPEECH_CLEANED"]


@pytest.mark.skipif(shutil.which("node") is None, reason="node is required for JS repair test")
def test_speech_transcript_repair_preserves_negation_measurements_and_station_ids() -> None:
    script = f"""
import {{ repairSpeechTranscript }} from {json.dumps(_REPAIR_MODULE.as_uri())};
const result = repairSpeechTranscript({json.dumps("No biopsies were performed in station four are. Lidocane 4 ml was used in the r u l.")});
console.log(JSON.stringify(result));
"""

    completed = subprocess.run(
        [shutil.which("node") or "node", "--input-type=module", "-e", script],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)
    repaired = payload["text"]
    assert repaired.startswith("No biopsies were performed")
    assert "station 4R" in repaired
    assert "lidocaine 4 mL" in repaired
    assert "RUL" in repaired


@pytest.mark.skipif(shutil.which("node") is None, reason="node is required for JS repair test")
def test_speech_transcript_repair_handles_robust_bundle_cases() -> None:
    cases = [
        {
            "name": "core bronchoscopy and station repair",
            "input": "e bus staging with rows positive at station for our. r u l lesion was sampled by t b n a using a twenty two gauge needle. broncho alveolar lavage from the left upper low with 30 cc normal saline and lido cane.",
            "expected": "EBUS staging with ROSE positive at station 4R. RUL lesion was sampled by TBNA using a 22-gauge needle. bronchoalveolar lavage from the left upper lobe with 30 mL normal saline and lidocaine.",
        },
        {
            "name": "avoid unsafe station homophones without side",
            "input": "The station for the procedure was moved. station to be used later. pain level seven out of ten.",
            "expected": "The station for the procedure was moved. station to be used later. pain level seven out of ten.",
        },
        {
            "name": "pleural procedure repair",
            "input": "thor a centesis for plural effusion with no new mo thorax. pleur x catheter placed.",
            "expected": "thoracentesis for pleural effusion with no pneumothorax. PleurX catheter placed.",
        },
        {
            "name": "device and specimen repair",
            "input": "Ion robotic bronchoscopy with combo ct and guide sheet. formal in and cyto light were sent.",
            "expected": "Ion robotic bronchoscopy with cone beam CT and guide sheath. formalin and CytoLyt were sent.",
        },
        {
            "name": "station word numbers and lobe repair",
            "input": "station one one are and station seven were sampled with EBUS. right middle love examined. level four left also sampled.",
            "expected": "station 11R and station 7 were sampled with EBUS. right middle lobe examined. station 4L also sampled.",
        },
    ]
    script = f"""
import {{ repairSpeechTranscript }} from {json.dumps(_REPAIR_MODULE.as_uri())};
const cases = {json.dumps(cases)};
const results = cases.map((item) => ({{
  name: item.name,
  text: repairSpeechTranscript(item.input).text,
  expected: item.expected,
}}));
console.log(JSON.stringify(results));
"""

    completed = subprocess.run(
        [shutil.which("node") or "node", "--input-type=module", "-e", script],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)
    for case in payload:
        assert case["text"] == case["expected"], case["name"]


@pytest.mark.skipif(shutil.which("node") is None, reason="node is required for JS repair test")
def test_speech_transcript_repair_fixes_reporter_navigation_and_ebus_terms() -> None:
    sample = (
        "Ion robotic bronchosby for leftover low 1.8 cm ground glass opacity navigation successful "
        "radial probe eccentric view tool lesion confirmed with combi-CT after cathart adjusted to concentric "
        "three needle biopsies with rows positive for a double cells followed by four cryoopsies with a 1.1 "
        "millimeter probe, even staging station 7, 5.1 millimeters, 4 passes with 22 gauge needle, rows negative, "
        "4L, 6.8 millimeters, 3 passes with 22 gauge needle, rows negative, no complications."
    )
    script = f"""
import {{ repairSpeechTranscript }} from {json.dumps(_REPAIR_MODULE.as_uri())};
const result = repairSpeechTranscript({json.dumps(sample)});
console.log(JSON.stringify(result));
"""

    completed = subprocess.run(
        [shutil.which("node") or "node", "--input-type=module", "-e", script],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)
    repaired = payload["text"]
    assert "bronchoscopy" in repaired
    assert "left upper lobe 1.8 cm ground glass opacity" in repaired
    assert "cone beam" in repaired
    assert "catheter adjusted to concentric" in repaired
    assert "with ROSE positive" in repaired
    assert "atypical cells" in repaired
    assert "cryobiopsies" in repaired
    assert "EBUS staging station 7" in repaired
    assert repaired.count("ROSE negative") == 2


@pytest.mark.skipif(shutil.which("node") is None, reason="node is required for JS repair test")
def test_speech_transcript_repair_fixes_ion_and_rul_lesion_phrase() -> None:
    sample = "Hi, I'm robotic bronchoscopy for 1.3 centimeter right up to low-veluation."
    script = f"""
import {{ repairSpeechTranscript }} from {json.dumps(_REPAIR_MODULE.as_uri())};
const result = repairSpeechTranscript({json.dumps(sample)});
console.log(JSON.stringify(result));
"""

    completed = subprocess.run(
        [shutil.which("node") or "node", "--input-type=module", "-e", script],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)
    repaired = payload["text"]
    assert repaired == "Ion robotic bronchoscopy for 1.3 centimeter right upper lobe lesion."


@pytest.mark.skipif(shutil.which("node") is None, reason="node is required for JS repair test")
def test_speech_transcript_repair_handles_recent_real_world_dictation_failures() -> None:
    cases = [
        {
            "name": "ebus guided staging",
            "input": "Monarch robotic bronchoscopy with hebus skydits staging.",
            "contains": ["Monarch robotic bronchoscopy", "EBUS guided staging"],
        },
        {
            "name": "ebus tbna granulomas and sarcoidosis",
            "input": "EVIS TBNA for meters panel and fed an op at the station 718 millimeters 5 passes with 22-gauge and 25-gauge needles ROSE showed granny aloma is consistent with sacriosis 4r was 14 millimeters 4 passes with 22-gauge ROSE showed granny aloma is 11 out 12 millimeters 3 passes with 22-gauge rose road, ship, granny, lumbar, airway inspection, normal, new complications.",
            "contains": [
                "EBUS-TBNA",
                "mediastinal lymphadenopathy",
                "station 7 18 millimeters",
                "granulomas consistent with sarcoidosis",
                "11L 12 millimeters",
                "no complications",
            ],
        },
        {
            "name": "cone beam ct and cryobiopsies",
            "input": "Robotic bronchoscopy, right lower lobe 3.1 centimeter mass navigation successful radial probe concentric on first attempt. Combating CT, confirmed tool in lesion, five needle aspirates, rows, positive for malignancy, followed by four cryovolopsies with 1.1 millimeter probe, staging evis station 7 9.1 millimeters, five passes with 22-gauge and 25-gauge needles ROSE adequate for our 7.3 millimeters, five passes with 22-gauge and 25-gauge needles rose malignant, 11r, 5.8 millimeter, three passes with 22-gauge ROSE adequate no complications.",
            "contains": [
                "cone beam CT",
                "ROSE, positive for malignancy",
                "cryobiopsies",
                "staging EBUS station 7 9.1 millimeters",
                "4R 7.3 millimeters",
                "11R, 5.8 millimeter",
            ],
        },
        {
            "name": "flexible bronchoscopy fluoroscopy and pneumothorax",
            "input": "Flex will bronch with BAL and transbronchial biopsy for suspected ILD BAL from right middle lobe, three aliquots, 60 mL each returned approximately 55% transbronchial biopsy from right lower lobe, time six with fluoresce B, small amount of bleeding controlled with suction, no neomorphoax on post-resver church s x-ray.",
            "contains": [
                "Flexible bronchoscopy",
                "BAL",
                "x 6 with fluoroscopy",
                "pneumothorax",
                "post-procedure chest x-ray",
            ],
        },
    ]

    script = f"""
import {{ repairSpeechTranscript }} from {json.dumps(_REPAIR_MODULE.as_uri())};
const cases = {json.dumps(cases)};
const results = cases.map((item) => ({{
  name: item.name,
  text: repairSpeechTranscript(item.input).text,
  contains: item.contains,
}}));
console.log(JSON.stringify(results));
"""

    completed = subprocess.run(
        [shutil.which("node") or "node", "--input-type=module", "-e", script],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)
    for case in payload:
        for expected in case["contains"]:
            assert expected in case["text"], f'{case["name"]}: missing {expected!r} in {case["text"]!r}'
