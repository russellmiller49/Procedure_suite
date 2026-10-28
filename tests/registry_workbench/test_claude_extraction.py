"""Offline tests for the Claude robotic_ebus_v1 extractor (no network).

The facts fixture is a hand-authored answer in the model's response format;
these tests exercise schema generation, assembly, anchoring and validation, not
model accuracy.
"""

import copy
import hashlib
import json
import uuid
from pathlib import Path

import pytest
from ip_registry_contracts.models import ExtractionRequest, ExtractionResponse
from ip_registry_engine.focused import prepare_text

from app.common.anthropic_client import (
    ClaudeClient,
    ClaudeSettings,
    build_params,
    estimate_cost_usd,
)
from app.common.llm_egress import EgressDenied, egress_context
from app.llm_extraction.anchoring import anchor
from app.llm_extraction.facts_schema import schema_complexity
from app.registry_workbench.extraction.assembler import Assembler
from app.registry_workbench.extraction.claude_provider import ClaudeRegistryProvider
from app.registry_workbench.extraction.contract_spec import (
    contract_spec,
    dictionary,
    dictionary_fields,
)
from app.registry_workbench.extraction.prompt import (
    EXCLUDED_QA_RULES,
    PROMPT_QA_RULES,
    system_prompt,
    user_message,
)

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures/registry_workbench"
TEXT = (FIXTURES / "rebus_demo_procedure.txt").read_text()
FACTS = json.loads((FIXTURES / "rebus_demo_facts.json").read_text())
DIGEST = hashlib.sha256(TEXT.encode()).hexdigest()


def assemble(facts, text=TEXT):
    return Assembler(
        source_text=text,
        prepared_text=prepare_text(text),
        source_document_id=str(uuid.uuid4()),
        source_digest=hashlib.sha256(text.encode()).hexdigest(),
        extractor_version="claude-opus-5-5/test",
    ).assemble(facts)


def fact(facts, local_id, field):
    for array in ("enum_facts", "bool_facts", "number_facts", "text_facts"):
        for item in facts[array]:
            if item["local_id"] == local_id and item["field"] == field:
                return item
    raise KeyError((local_id, field))


def provenance(proposal, path):
    return next(p for p in proposal["field_provenance"] if p["field_path"] == path)


# -- schema and prompt --------------------------------------------------------


def test_facts_schema_fits_structured_output_limits():
    schema = contract_spec().schema()
    assert schema_complexity(schema) == {"optional_properties": 0, "union_parameters": 0}
    assert schema == contract_spec().schema()


def test_every_extractable_field_is_a_dictionary_field():
    known = set(dictionary_fields())
    for path in contract_spec().fields:
        if not path.startswith("revision."):
            assert path in known, path


def test_every_dictionary_qa_rule_is_prompted_or_excluded():
    ids = {rule["Rule ID"] for rule in dictionary()["qa_rules"]}
    assert set(PROMPT_QA_RULES).isdisjoint(EXCLUDED_QA_RULES)
    assert set(PROMPT_QA_RULES) | set(EXCLUDED_QA_RULES) == ids


def test_system_prompt_is_deterministic_and_carries_dictionary_text():
    prompt = system_prompt()
    assert prompt == system_prompt.__wrapped__()
    assert "Bronchus visibly leading to or entering lesion." in prompt
    assert "Q041:" in prompt and "Q030:" not in prompt


def test_outcome_label_lines_never_reach_the_model():
    text = TEXT + "\nSynthetic downstream pathology label: adenocarcinoma\n"
    request = ExtractionRequest(
        job_id=uuid.uuid4(),
        source_document_id=uuid.uuid4(),
        source_digest=hashlib.sha256(text.encode()).hexdigest(),
        text=text,
        kind="procedure",
    )
    params = ClaudeRegistryProvider(ClaudeClient(sdk=object())).build_params(request)
    assert "adenocarcinoma" not in params["messages"][0]["content"]


# -- assembly ----------------------------------------------------------------


def test_fixture_assembles_into_a_valid_approvable_revision():
    result = assemble(FACTS)
    assert result.valid and result.approval_errors == []
    proposal = result.proposal
    lung, node = proposal["targets"]
    assert (lung["site"], lung["lobe"], lung["max_diameter_mm"]) == ("lung", "RUL", 18.0)
    assert (node["iaslc_station"], node["short_axis_mm"], node["size_axis_explicit"]) == (
        "7",
        10.0,
        True,
    )
    surveys = {s["iaslc_station"]: s for s in proposal["station_surveys"]}
    assert surveys["4R"]["station_sampled"] is False and surveys["7"]["station_sampled"] is True
    assert proposal["localization_events"][1]["tool_lesion_relationship"] == "TIL"
    assert [e["event_sequence_number"] for e in proposal["localization_events"]] == [1, 2]
    aggregate = proposal["sampling_acquisitions"][0]
    assert aggregate["reported_pass_count"] == 4 and aggregate["attribution_status"] == "attributed"
    assert "pass_sequence_number" not in aggregate
    assert proposal["complication_assessment"] == "absent"


def test_every_excerpt_is_an_exact_source_slice():
    proposal = assemble(FACTS).proposal
    spans = [p for p in proposal["field_provenance"] if "source_start" in p]
    assert spans
    for item in spans:
        assert TEXT[item["source_start"] : item["source_end"]] == item["source_excerpt"]


def test_duplicate_quote_anchors_near_its_row():
    proposal = assemble(FACTS).proposal
    lobe = provenance(proposal, "/targets/0/lobe")
    row_anchor = TEXT.index("prespecified target T1")
    assert lobe["source_start"] > row_anchor > TEXT.index("right upper lobe")


def test_planned_and_uncertain_statements_never_set_values():
    facts = copy.deepcopy(FACTS)
    fact(facts, "T1", "targets.bronchus_sign_present")["assertion"] = "planned"
    result = assemble(facts)
    assert "bronchus_sign_present" not in result.proposal["targets"][0]
    assert any(u["kind"] == "planned_only" for u in result.unresolved)


def test_unanchored_evidence_is_dropped():
    facts = copy.deepcopy(FACTS)
    fact(facts, "T1", "targets.max_diameter_mm")["evidence_quote"] = "a 25 mm spiculated lesion"
    result = assemble(facts)
    assert "max_diameter_mm" not in result.proposal["targets"][0]
    assert result.stats["facts_unanchored"] == 1


def test_short_axis_without_explicit_axis_becomes_a_blocking_conflict():
    facts = copy.deepcopy(FACTS)
    facts["bool_facts"] = [
        f for f in facts["bool_facts"] if f["field"] != "targets.size_axis_explicit"
    ]
    result = assemble(facts)
    assert result.valid
    assert "short_axis_mm" not in result.proposal["targets"][1]
    entry = provenance(result.proposal, "/targets/1/short_axis_mm")
    assert entry["conflict_status"] == "unresolved" and entry["raw_value"] == "10.0"
    assert result.approval_errors == ["unresolved_field_conflict"]


def test_til_without_volumetric_confirmation_becomes_a_conflict():
    facts = copy.deepcopy(FACTS)
    fact(facts, "L2", "localization_events.confirmation_basis")["value"] = "fluoroscopy"
    result = assemble(facts)
    assert result.valid
    assert "tool_lesion_relationship" not in result.proposal["localization_events"][1]
    assert "unresolved_field_conflict" in result.approval_errors


def test_inspected_station_with_sampling_results_is_flagged_on_the_survey():
    facts = copy.deepcopy(FACTS)
    fact(facts, "S7", "station_surveys.station_sampled").update(value=False, assertion="negated")
    result = assemble(facts)
    assert result.valid
    assert "station_sampled" not in result.proposal["station_surveys"][0]
    assert (
        provenance(result.proposal, "/station_surveys/0/station_sampled")["conflict_status"]
        == "unresolved"
    )


def test_rows_missing_required_parents_cascade_out():
    facts = copy.deepcopy(FACTS)
    facts["rows"] = [r for r in facts["rows"] if r["local_id"] != "ES1"]
    for array in ("enum_facts", "bool_facts"):
        facts[array] = [f for f in facts[array] if f["local_id"] != "ES1"]
    result = assemble(facts)
    assert result.valid
    assert result.proposal["station_surveys"] == []
    assert all("ebus_session_id" not in t for t in result.proposal["targets"])


def test_no_procedure_component_is_unsupported():
    result = assemble({"rows": [], "unresolved": []})
    assert result.errors == ["no_procedure_component"]


def test_anchor_rejects_paraphrase_and_accepts_whitespace_drift():
    assert anchor(TEXT, "the needle was confirmed inside the nodule") is None
    span = anchor(TEXT, "Mobile  cone-beam CT\nthen confirmed")
    assert span is not None and TEXT[span.start : span.end].startswith("Mobile cone-beam CT")


# -- client and provider -------------------------------------------------------


class _Stream:
    def __init__(self, message):
        self.message = message

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def get_final_message(self):
        return self.message


class _FakeMessages:
    def __init__(self, replies):
        self.replies, self.calls = list(replies), []

    def stream(self, **params):
        self.calls.append(params)
        return _Stream(self.replies.pop(0))


class _FakeSDK:
    def __init__(self, replies):
        self.messages = _FakeMessages(replies)
        self.beta = type("Beta", (), {"messages": self.messages})()


def _message(payload, *, model="claude-opus-5-5", stop="end_turn"):
    return {
        "id": "msg_test",
        "model": model,
        "stop_reason": stop,
        "content": [
            {"type": "thinking", "thinking": ""},
            {"type": "text", "text": json.dumps(payload)},
        ],
        "usage": {
            "input_tokens": 900,
            "output_tokens": 2500,
            "cache_read_input_tokens": 7000,
            "cache_creation": {"ephemeral_5m_input_tokens": 0, "ephemeral_1h_input_tokens": 0},
        },
    }


def _request(text=TEXT, kind="procedure"):
    return ExtractionRequest(
        job_id=uuid.uuid4(),
        source_document_id=uuid.uuid4(),
        source_digest=hashlib.sha256(text.encode()).hexdigest(),
        text=text,
        kind=kind,
    )


def test_request_parameters_are_cached_and_never_send_sampling_controls():
    params = build_params(ClaudeSettings(), system="S", user="U", schema={"type": "object"})
    assert params["system"][0]["cache_control"] == {"type": "ephemeral", "ttl": "1h"}
    assert params["output_config"] == {
        "effort": "medium",
        "format": {"type": "json_schema", "schema": {"type": "object"}},
    }
    assert not {"temperature", "top_p", "top_k", "thinking"} & set(params)


def test_egress_is_denied_without_declared_synthetic_provenance():
    sdk = _FakeSDK([_message(FACTS)])
    with pytest.raises(EgressDenied):
        ClaudeRegistryProvider(ClaudeClient(ClaudeSettings(), sdk=sdk)).extract(_request())
    assert sdk.messages.calls == []


def test_provider_returns_a_proposed_response_with_inference_metadata():
    sdk = _FakeSDK([_message(FACTS)])
    with egress_context("synthetic", source="test"):
        response = ClaudeRegistryProvider(ClaudeClient(ClaudeSettings(), sdk=sdk)).extract(
            _request()
        )
    assert isinstance(response, ExtractionResponse)
    assert response.status == "proposed"
    call = sdk.messages.calls[0]
    assert call["betas"] == ["server-side-fallback-2026-07-01"] and call["fallbacks"] == "default"
    inference = response.observations["inference"]
    assert inference["model"] == "claude-opus-5-5" and not inference["repair_used"]
    assert inference["cost_usd"] == pytest.approx(
        estimate_cost_usd(
            "claude-opus-5-5",
            {"input_tokens": 900, "output_tokens": 2500, "cache_read_input_tokens": 7000},
        )
    )


def test_unfixable_answer_triggers_one_stateless_repair_call(monkeypatch):
    broken = copy.deepcopy(FACTS)
    fact(broken, "P_RB", "procedures.performance")["value"] = "unknown"
    # Simulate a link error the deterministic fixes cannot resolve.
    monkeypatch.setattr(Assembler, "_fix_link", lambda self, code: False)
    sdk = _FakeSDK([_message(broken), _message(FACTS)])
    with egress_context("synthetic", source="test"):
        response = ClaudeRegistryProvider(ClaudeClient(ClaudeSettings(), sdk=sdk)).extract(
            _request()
        )
    assert response.status == "proposed" and response.observations["inference"]["repair_used"]
    first, repair = sdk.messages.calls
    assert repair["system"] == first["system"] and len(repair["messages"]) == 1
    content = repair["messages"][0]["content"]
    assert (
        "navigation_requires_started_robotic_component" in content
        and "<previous_answer>" in content
    )


def test_refusal_is_degraded_not_raised():
    sdk = _FakeSDK([_message({}, stop="refusal")])
    with egress_context("synthetic", source="test"):
        response = ClaudeRegistryProvider(ClaudeClient(ClaudeSettings(), sdk=sdk)).extract(
            _request()
        )
    assert response.status == "degraded" and "model_inference_failed" in response.warnings
    assert response.observations["proposal"] is None


def test_non_procedure_documents_use_the_local_engine():
    sdk = _FakeSDK([])
    pathology = "Specimen A, right upper lobe: adenocarcinoma. Final diagnosis."
    with egress_context("synthetic", source="test"):
        response = ClaudeRegistryProvider(ClaudeClient(ClaudeSettings(), sdk=sdk)).extract(
            _request(pathology, kind="pathology")
        )
    assert sdk.messages.calls == [] and response.status in {"proposed", "degraded", "unsupported"}


def test_user_message_wraps_the_document():
    assert user_message("note").endswith("<document>\nnote\n</document>")
