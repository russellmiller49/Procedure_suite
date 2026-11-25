"""Truth-first corpus: generation, gold integrity, verification, scoring, qualification."""

import copy
import hashlib
import json
import uuid

import pytest

from app.common.anthropic_client import ClaudeClient, ClaudeSettings
from app.registry_workbench.scoring import aggregate, score_document, wilson_lower
from ops.tools.robotic_ebus_truth import build_split, claude_writer, qualify_truth
from ops.tools.robotic_ebus_truth.gold import build_gold, plan_statements
from ops.tools.robotic_ebus_truth.scenarios import TRAPS, sample_scenario
from ops.tools.robotic_ebus_truth.template_writer import STYLES, render
from ops.tools.robotic_ebus_truth.verify import (
    unsupported_values,
    value_supported,
    verifier_accepts,
)


def _document(seed, style="sectioned"):
    scenario = sample_scenario(seed)
    stated = plan_statements(scenario, seed)
    text, spans = render(scenario, stated, style, seed)
    digest = hashlib.sha256(text.encode()).hexdigest()
    gold = build_gold(scenario, stated, spans, text, document_id=str(uuid.uuid4()), digest=digest)
    return scenario, stated, text, spans, gold


def _seed_with(trap):
    return next(seed for seed in range(2000) if trap in sample_scenario(seed).traps)


def test_sampling_is_deterministic():
    a, b = sample_scenario(42), sample_scenario(42)
    assert [(u.id, u.sets) for u in a.units] == [(u.id, u.sets) for u in b.units]


@pytest.mark.parametrize("style", STYLES)
def test_every_style_yields_valid_gold_with_exact_quotes(style):
    for seed in range(40):
        scenario, stated, text, spans, gold = _document(seed, style)
        assert text.startswith("SYNTHETIC TRAINING NOTE - NOT FOR CLINICAL USE")
        assert unsupported_values(scenario, stated, spans, text) == []
        for entry in gold["field_provenance"]:
            if entry.get("source_start") is not None:
                assert text[entry["source_start"] : entry["source_end"]] == entry["source_excerpt"]


def test_every_trap_occurs():
    seen = {t for seed in range(400) for t in sample_scenario(seed).traps}
    assert seen == set(TRAPS)


def test_til_from_radial_ebus_alone_is_not_gold_til():
    *_, text, _, gold = _document(_seed_with("til_without_volumetric"))
    assert "confirming tool-in-lesion" in text
    assert all(e.get("tool_lesion_relationship") is None for e in gold["localization_events"])


def test_planned_only_ebus_has_no_ebus_rows():
    *_, gold = _document(_seed_with("planned_only_ebus"))
    ebus = next(p for p in gold["procedures"] if p["category"] == "linear_ebus")
    assert (ebus["performance"], ebus["completion"], ebus["planned"]) == (
        "not_performed",
        "not_started",
        True,
    )
    assert gold["ebus_sessions"] == [] and gold["station_surveys"] == []


def test_surveyed_not_sampled_station_has_no_node_target():
    *_, gold = _document(_seed_with("surveyed_not_sampled"))
    inspected = {
        s["iaslc_station"] for s in gold["station_surveys"] if s["station_sampled"] is False
    }
    nodes = {t["iaslc_station"] for t in gold["targets"] if t["site"] == "lymph_node"}
    assert inspected and not inspected & nodes


def test_historical_stations_never_enter_gold():
    scenario, _, text, _, gold = _document(_seed_with("historical_mention"))
    unit = next(u for u in scenario.units if u.kind == "history")
    assert f"station {unit.params['station']}" in text and unit.sets == []


def test_value_check_rejects_a_changed_number():
    assert value_supported("max_diameter_mm", 18.0, "an 18 mm solid lesion")
    assert value_supported("max_diameter_mm", 18.0, "a 1.8 cm solid lesion")
    assert not value_supported("max_diameter_mm", 18.0, "a 13 mm solid lesion")
    assert value_supported("bronchus_sign_present", False, "There was no bronhcus sign.")


def test_split_builder_writes_sealed_test_gold_and_refuses_overwrite(tmp_path):
    out = tmp_path / "corpus"
    manifest = build_split.build(out, families=12, seed=900, writer="template")
    assert manifest["rejected_documents"] == 0
    assert (
        "sealed/test.gold.jsonl" in manifest["sealed"]
        and not (out / "gold" / "test.gold.jsonl").exists()
    )
    splits_by_family = {}
    for split in ("train", "validation", "test"):
        for line in (out / f"{split}.jsonl").read_text().splitlines():
            row = json.loads(line)
            assert splits_by_family.setdefault(row["family_id"], split) == split
    with pytest.raises(SystemExit):
        build_split.build(out, families=1, seed=1, writer="template")


def test_gold_scores_perfectly_against_itself_and_zero_when_empty():
    golds = [_document(seed)[-1] for seed in range(15)]
    perfect = aggregate([score_document(g, copy.deepcopy(g)) for g in golds])
    assert perfect["overall"]["precision"] == 1.0 and perfect["overall"]["recall"] == 1.0
    assert perfect["foreign_key_accuracy"]["rate"] == 1.0
    empty = aggregate([score_document(g, None) for g in golds])
    assert empty["overall"]["recall"] == 0.0 and empty["overall"]["fp"] == 0


def test_scorer_counts_wrong_values_false_fills_and_misses():
    gold = next(
        g
        for g in (_document(s)[-1] for s in range(200))
        if any(t["site"] == "lung" for t in g["targets"])
    )
    predicted = copy.deepcopy(gold)
    lung = next(t for t in predicted["targets"] if t["site"] == "lung")
    lung["lesion_attenuation_type"] = (
        None if gold["targets"][0].get("lesion_attenuation_type") else "solid"
    )
    lung["pet_description"] = "invented PET text"
    score = score_document(gold, predicted)
    assert score.fields["targets.pet_description"] == [0, 1, 0]
    assert sum(score.fields["targets.lesion_attenuation_type"][1:]) == 1


def test_scorer_ignores_contract_defaults():
    gold = _document(3)[-1]
    predicted = copy.deepcopy(gold)
    predicted["complication_assessment"] = gold["complication_assessment"]
    for row in predicted["specimens"]:
        row.setdefault("target_attribution_status", "unallocated")
    assert aggregate([score_document(gold, predicted)])["overall"]["fp"] == 0


def test_wilson_lower_bound():
    assert wilson_lower(0, 0) is None
    assert 0.83 < wilson_lower(20, 20) < 0.84


def test_qualification_reserves_the_test_split_once(tmp_path):
    corpus = tmp_path / "corpus"
    build_split.build(corpus, families=10, seed=300, writer="template")
    report = qualify_truth.qualify(corpus, "deterministic", tmp_path / "q.json")
    assert (corpus / qualify_truth.LEDGER).exists() and report["promotion_allowed"] is False
    with pytest.raises(ValueError):
        qualify_truth.qualify(corpus, "deterministic", tmp_path / "q2.json")


def test_qualification_refuses_a_tampered_sealed_split(tmp_path):
    corpus = tmp_path / "corpus"
    build_split.build(corpus, families=10, seed=301, writer="template")
    sealed = corpus / "sealed" / "test.gold.jsonl"
    sealed.write_text(sealed.read_text() + "\n")
    with pytest.raises(ValueError):
        qualify_truth.qualify(corpus, "deterministic", tmp_path / "q.json")
    assert not (corpus / qualify_truth.LEDGER).exists()


# -- Claude writer (offline) ---------------------------------------------------


class _Stream:
    def __init__(self, message):
        self.message = message

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def get_final_message(self):
        return self.message


class _FakeSDK:
    def __init__(self, replies):
        self.replies, self.calls = list(replies), []
        self.messages = self
        self.beta = self

    def stream(self, **params):
        self.calls.append(params)
        reply = self.replies.pop(0)
        return _Stream(
            {
                "id": "m",
                "model": params["model"],
                "stop_reason": "end_turn",
                "content": [{"type": "text", "text": json.dumps(reply)}],
                "usage": {},
            }
        )


def _draft(seed):
    scenario = sample_scenario(seed)
    stated = plan_statements(scenario, seed)
    facts = claude_writer.facts(scenario, stated, seed)
    note = "SYNTHETIC TRAINING NOTE - NOT FOR CLINICAL USE\n" + "\n".join(
        statement for _, statement, _ in facts
    )
    quotes = [{"fact_id": fid, "quote": statement} for fid, statement, _ in facts]
    return scenario, stated, facts, {"note": note, "quotes": quotes}


def test_claude_draft_is_accepted_only_with_quotes_and_a_clean_verifier():
    from app.common.llm_egress import egress_context

    scenario, stated, facts, draft = _draft(17)
    verdict = {
        "facts": [{"fact_id": fid, "verdict": "supported"} for fid, _, _ in facts],
        "extra_facts": [],
    }
    client = ClaudeClient(ClaudeSettings(), sdk=_FakeSDK([draft, verdict]))
    with egress_context("synthetic", source="test"):
        result = claude_writer.write_online(client, scenario, stated, style="dictation", seed=17)
    assert result["accepted"] and result["problems"] == []
    gold = build_gold(
        scenario,
        stated,
        result["spans"],
        result["text"],
        document_id=str(uuid.uuid4()),
        digest=hashlib.sha256(result["text"].encode()).hexdigest(),
    )
    assert gold["procedures"]


def test_claude_draft_missing_a_quote_is_rejected_before_the_verifier():
    from app.common.llm_egress import egress_context

    scenario, stated, facts, draft = _draft(18)
    draft["quotes"][0]["quote"] = "a sentence that is not in the note"
    sdk = _FakeSDK([draft])
    with egress_context("synthetic", source="test"):
        result = claude_writer.write_online(
            ClaudeClient(ClaudeSettings(), sdk=sdk), scenario, stated, style="messy", seed=18
        )
    assert not result["accepted"] and result["problems"][0].startswith("quote_not_found")
    assert len(sdk.calls) == 1


def test_verifier_rejects_contradictions_and_extra_facts():
    ok, problems = verifier_accepts(
        {
            "facts": [{"fact_id": "F1", "verdict": "contradicted"}],
            "extra_facts": ["station 4L sampled"],
        },
        {"F1", "F2"},
    )
    assert not ok and {"F1:contradicted", "F2:missing", "extra:station 4L sampled"} <= set(problems)


def test_writer_prompt_never_leaks_other_cases_details():
    scenario, stated, facts, _ = _draft(19)
    message = claude_writer.writer_message(
        scenario, facts, style="narrative", example="EXAMPLE TEXT"
    )
    assert "Copy none of its clinical details" in message and all(
        f"[{fid}]" in message for fid, _, _ in facts
    )


def test_scorer_aligns_specimens_whether_or_not_the_label_keeps_the_word_specimen():
    gold = next(
        g for g in (_document(s)[-1] for s in range(200)) if len(g.get("specimens") or []) >= 2
    )
    predicted = copy.deepcopy(gold)
    for row in predicted["specimens"]:
        row["specimen_label"] = f"Specimen {row['specimen_label']}"
    score = score_document(gold, predicted)
    result = aggregate([score])
    assert result["overall"]["fp"] == 0 and result["overall"]["fn"] == 0
    assert score.foreign_keys[0] == score.foreign_keys[1]
    # A different specimen is still a different specimen.
    predicted["specimens"][0]["specimen_label"] = "Specimen ZZ"
    assert aggregate([score_document(gold, predicted)])["overall"]["fp"] > 0
