"""Offline tests for the Batch API helpers and evaluation scoring."""

from types import SimpleNamespace

import pytest

from app.common.llm_egress import EgressDenied, egress_context
from app.llm_extraction import batch
from ops.tools.eval_registry_llm import score, silver_facts


class _Batches:
    def __init__(self):
        self.created, self.polls = None, 0

    def create(self, requests):
        self.created = requests
        return SimpleNamespace(id="msgbatch_1")

    def retrieve(self, batch_id):
        self.polls += 1
        status = "ended" if self.polls > 1 else "in_progress"
        return SimpleNamespace(processing_status=status, request_counts={})

    def results(self, batch_id):
        ok = SimpleNamespace(type="succeeded", message={"id": "m1"})
        return [
            SimpleNamespace(custom_id="d1", result=SimpleNamespace(type="errored")),
            SimpleNamespace(custom_id="d0", result=ok),
        ]


def _sdk():
    return SimpleNamespace(messages=SimpleNamespace(batches=_Batches()))


def test_batch_submission_requires_egress_and_valid_ids():
    sdk = _sdk()
    with pytest.raises(EgressDenied):
        batch.submit(sdk, [("d0", {})])
    with egress_context("synthetic", source="test"):
        with pytest.raises(ValueError):
            batch.submit(sdk, [("doc:1", {})])
        assert batch.submit(sdk, [("d0", {"model": "m"})]) == "msgbatch_1"
    assert sdk.messages.batches.created == [{"custom_id": "d0", "params": {"model": "m"}}]


def test_batch_results_are_keyed_by_custom_id_not_order():
    sdk = _sdk()
    batch.wait(sdk, "msgbatch_1", poll_seconds=0, sleep=lambda s: None)
    messages, errors = batch.collect(sdk, "msgbatch_1")
    assert messages == {"d0": {"id": "m1"}} and errors == {"d1": "errored"}


def test_silver_scores_only_fields_the_metadata_describes():
    meta = {"lobe": "LLL", "lesion_size_mm": 15, "bronchus_sign": "positive", "complication": "none"}
    expected = silver_facts(meta)
    assert expected == {
        "target.lobe": {"LLL"},
        "target.max_diameter_mm": {"LLL:15"},
        "target.bronchus_sign": {"LLL:true"},
        "safety.immediate": {"absent"},
    }
    results = {"doc": {"facts": {"target.lobe": ["LLL"], "ebus.sampled_station": ["7"]}}}
    report = score(results, {"doc": expected}, ("target.lobe", "ebus.sampled_station"), known_only=True)
    assert report["overall"]["false_positive"] == 0 and report["overall"]["true_positive"] == 1
