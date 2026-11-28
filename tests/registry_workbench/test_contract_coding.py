"""Suggested codes from robotic_ebus_v1 contract facts (hand-checked cases + gold invariants)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from app.registry_workbench.contract_coding import (
    provenance_from_evidence_map,
    suggest_codes,
    to_registry_record,
)

CORPUS = Path("data/ml_training/robotic_ebus_v1/corpus_truth_20261109")


class Case:
    """Small builder for contract proposals with positional provenance."""

    def __init__(self, *, ebus: bool = True, robotic: bool = True) -> None:
        self.text = ""
        self.p: dict[str, Any] = {
            "procedures": [],
            "targets": [],
            "ebus_sessions": [],
            "station_surveys": [],
            "navigation_runs": [],
            "localization_events": [],
            "sampling_acquisitions": [],
            "field_provenance": [],
        }
        if robotic:
            self._row(
                "procedures", {"category": "robotic_bronchoscopy", "performance": "performed"}
            )
        if ebus:
            self._row("procedures", {"category": "linear_ebus", "performance": "performed"})
            self.p["ebus_sessions"].append({"ebus_session_id": "ebus"})
        self._n = 0

    def _row(
        self, collection: str, row: dict[str, Any], quote: str | None = None, **prov: Any
    ) -> int:
        rows = self.p[collection]
        rows.append(row)
        index = len(rows) - 1
        if quote is not None:
            start = len(self.text)
            self.text += quote + " "
            for name in row:
                self.p["field_provenance"].append(
                    {
                        "field_path": f"/{collection}/{index}/{name}",
                        "source_start": start,
                        "source_end": start + len(quote),
                        "source_excerpt": quote,
                        "conflict_status": "none",
                        "assertion_context": "active",
                        **prov,
                    }
                )
        return index

    def _id(self, prefix: str) -> str:
        self._n += 1
        return f"{prefix}{self._n}"

    def station(
        self,
        station: str,
        *,
        sampled: bool | None,
        tool: str | None = "aspiration_needle",
        node: bool = True,
        **prov: Any,
    ) -> None:
        survey_id = self._id("survey")
        verb = "sampled" if sampled else "surveyed only"
        quote = f"Station {station} was {verb}."
        self._row(
            "station_surveys",
            {
                "station_survey_id": survey_id,
                "ebus_session_id": "ebus",
                "iaslc_station": station,
                "station_surveyed": True,
                "station_sampled": sampled,
            },
            quote,
            **prov,
        )
        if sampled and node:
            target_id = self._id("node")
            self._row(
                "targets",
                {
                    "target_id": target_id,
                    "site": "lymph_node",
                    "iaslc_station": station,
                    "station_survey_id": survey_id,
                    "ebus_session_id": "ebus",
                    "sampling_attempted": True,
                    "puncture_route": "EBUS",
                },
                quote,
            )
            if tool:
                self.sample(target_id, tool, f"Station {station}: three passes with a needle.")

    def lesion(
        self,
        lobe: str | None,
        segment: str | None = None,
        *,
        site: str = "lung",
        navigate: bool = True,
        radial: str | None = None,
        ebus_session: bool = False,
    ) -> str:
        target_id = self._id("lesion")
        row = {
            "target_id": target_id,
            "site": site,
            "anatomic_label": f"{lobe or 'central'} lesion",
        }
        if lobe:
            row["lobe"] = lobe
        if segment:
            row["segment"] = segment
        if ebus_session:
            row["ebus_session_id"] = "ebus"
        self._row("targets", row, f"Target in the {lobe or 'mediastinum'}.")
        if navigate:
            self._row(
                "navigation_runs",
                {
                    "navigation_run_id": self._id("run"),
                    "target_id": target_id,
                    "run_sequence_number": 1,
                    "platform_family": "Ion",
                    "navigation_run_outcome": "reached_and_sampled",
                },
                f"Ion navigation to the {lobe} target was successful.",
            )
        if radial:
            self._row(
                "localization_events",
                {
                    "localization_event_id": self._id("loc"),
                    "target_id": target_id,
                    "event_sequence_number": 1,
                    "localization_modality": "radial_EBUS",
                    "radial_ebus_view": radial,
                },
                f"Radial EBUS showed a {radial} view in the {lobe}.",
            )
        return target_id

    def sample(
        self, target_id: str | None, tool: str, quote: str, status: str = "attributed", **prov: Any
    ) -> None:
        row = {
            "sampling_pass_id": self._id("pass"),
            "acquisition_record_granularity": "aggregate_reported",
            "sampling_tool": tool,
            "attribution_status": status,
        }
        if target_id:
            row["target_id"] = target_id
        self._row("sampling_acquisitions", row, quote, **prov)

    def codes(self) -> dict[str, dict[str, Any]]:
        out = suggest_codes(self.p, source_text=self.text)
        self.result = out
        return {c["code"]: c for c in out["codes"]}


def test_two_sampled_stations_and_one_surveyed_gives_31652_with_both_quotes():
    case = Case(robotic=False)
    case.station("4R", sampled=True)
    case.station("7", sampled=True)
    case.station("11L", sampled=False)
    codes = case.codes()
    assert set(codes) == {"31652"}
    labels = [e["label"] for e in codes["31652"]["evidence"]]
    assert labels == ["Station 4R sampled", "Station 7 sampled"]
    assert all(case.text[e["start"] : e["end"]] == e["quote"] for e in codes["31652"]["evidence"])
    excluded = codes["31652"]["excluded"]
    assert [x["label"] for x in excluded] == ["Station 11L surveyed"]
    assert excluded[0]["reason"] == "surveyed, not sampled"
    assert codes["31652"]["needs_review"] is False


def test_three_sampled_stations_gives_31653():
    case = Case(robotic=False)
    for station in ("4R", "7", "11R"):
        case.station(station, sampled=True)
    assert set(case.codes()) == {"31653"}


def test_survey_only_ebus_gives_no_nodal_code():
    case = Case(robotic=False)
    case.station("4R", sampled=False)
    case.station("7", sampled=False)
    assert case.codes() == {}
    assert any(f["flag"] == "no_station_sampled" for f in case.result["review_flags"])


def test_planned_only_ebus_gives_no_nodal_code():
    case = Case(ebus=False)
    case.p["procedures"].append({"category": "linear_ebus", "performance": "not_performed"})
    case.station("4R", sampled=True)  # facts on a component that never started must not count
    target = case.lesion("RUL", radial="concentric")
    case.sample(target, "forceps", "Five forceps biopsies of the RUL target.")
    codes = case.codes()
    assert not ({"31652", "31653"} & set(codes))
    assert {"31628", "31627", "31654"} <= set(codes)


def test_navigation_radial_and_biopsy_in_two_lobes():
    case = Case(ebus=False)
    for lobe in ("RUL", "LLL"):
        target = case.lesion(lobe, radial="eccentric")
        case.sample(target, "forceps", f"Forceps biopsies of the {lobe} target.")
    codes = case.codes()
    assert set(codes) == {"31627", "31628", "31632", "31654"}
    assert codes["31632"]["units"] == 1
    assert len(codes["31628"]["evidence"]) == 2


def test_three_lobes_gives_two_additional_lobe_units():
    case = Case(ebus=False)
    for lobe in ("RUL", "RML", "LLL"):
        target = case.lesion(lobe)
        case.sample(target, "forceps", f"Forceps biopsies of the {lobe} target.")
    codes = case.codes()
    assert codes["31632"]["units"] == 2
    assert codes["31628"]["units"] == 1


def test_two_targets_in_one_lobe_gives_no_additional_lobe_code():
    case = Case(ebus=False)
    for segment in ("apical segment", "posterior segment"):
        target = case.lesion("RUL", segment)
        case.sample(target, "cryoprobe", f"Cryobiopsy of the RUL {segment} target.")
    codes = case.codes()
    assert "31628" in codes and "31632" not in codes


def test_peripheral_needle_alone_gives_31629_without_modifier():
    case = Case(ebus=False)
    target = case.lesion("LUL", "apicoposterior segment")
    case.sample(target, "aspiration_needle", "Four needle passes of the LUL target.")
    codes = case.codes()
    assert codes["31629"]["modifiers"] == []


def test_peripheral_needle_with_ebus_keeps_31629_with_59_and_shows_both_sites():
    case = Case()
    case.station("4R", sampled=True)
    target = case.lesion("LUL", "apicoposterior segment", radial="concentric")
    case.sample(target, "aspiration_needle", "Four needle passes of the LUL target.")
    codes = case.codes()
    assert {"31629", "31652", "31627", "31654"} == set(codes)
    assert codes["31629"]["modifiers"] == ["59"]
    labels = [e["label"] for e in codes["31629"]["evidence"]]
    assert any(label.startswith("Needle sampling, LUL") for label in labels)
    assert "Station 4R sampled" in labels


def test_peripheral_needle_without_a_lobe_is_bundled_into_ebus():
    case = Case()
    case.station("7", sampled=True)
    target = case.lesion(None)
    case.sample(target, "aspiration_needle", "Needle passes of the lung nodule.")
    codes = case.codes()
    assert "31629" not in codes and "31652" in codes
    assert any(d["code"] == "31629" for d in case.result["dropped"])


def test_brush_and_bal_map_and_fiducial_is_not_assessed():
    case = Case(ebus=False)
    target = case.lesion("RLL")
    case.sample(target, "brush", "Brushings of the RLL target.")
    case.sample(target, "BAL", "Lavage of the RLL.")
    codes = case.codes()
    assert {"31623", "31624"} <= set(codes)
    assert "31626" not in codes
    assert any("31626" in item["codes"] for item in case.result["not_assessed"])


def test_unattributed_and_unresolved_sampling_never_drive_a_code():
    case = Case(ebus=False)
    target = case.lesion("RUL")
    case.sample(None, "forceps", "Forceps biopsies were taken.", status="unallocated")
    case.sample(
        target, "aspiration_needle", "Needle or forceps, unclear.", conflict_status="unresolved"
    )
    codes = case.codes()
    assert not ({"31628", "31629"} & set(codes))
    assert any(f["flag"] == "sampling_not_attributed" for f in case.result["review_flags"])
    assert any(f["flag"] == "addon_without_primary" for f in case.result["review_flags"])


def test_survey_disagreement_is_not_counted_and_is_flagged():
    case = Case(robotic=False)
    case.station("4R", sampled=True)
    case.station("7", sampled=True)
    survey = next(s for s in case.p["station_surveys"] if s["iaslc_station"] == "7")
    survey["station_sampled"] = False
    codes = case.codes()
    assert set(codes) == {"31652"}
    assert [e["label"] for e in codes["31652"]["evidence"]] == ["Station 4R sampled"]
    assert codes["31652"]["needs_review"] is True


def test_structure_sampled_alongside_stations_is_flagged_for_review():
    case = Case(robotic=False)
    case.station("4R", sampled=True)
    case.station("7", sampled=True)
    mass = case.lesion(None, site="central_mass", navigate=False, ebus_session=True)
    case.sample(mass, "aspiration_needle", "Needle passes of the paratracheal mass.")
    codes = case.codes()
    assert set(codes) == {"31652"}
    assert codes["31652"]["needs_review"] is True


def test_structure_alone_counts_and_is_flagged():
    case = Case(robotic=False)
    mass = case.lesion(None, site="central_mass", navigate=False, ebus_session=True)
    case.sample(mass, "aspiration_needle", "Needle passes of the subcarinal mass.")
    codes = case.codes()
    assert set(codes) == {"31652"}
    assert codes["31652"]["needs_review"] is True


def _gold_rows():
    notes = {}
    for split in ("train", "validation"):
        for line in (CORPUS / f"{split}.jsonl").read_text().splitlines():
            row = json.loads(line)
            notes[row.get("document_id") or row.get("id")] = row.get("text")
        for line in (CORPUS / "gold" / f"{split}.gold.jsonl").read_text().splitlines():
            yield json.loads(line), notes


@pytest.mark.skipif(not (CORPUS / "gold").exists(), reason="truth corpus not present")
def test_gold_invariants_for_nodal_only_and_lobe_counts():
    checked = 0
    for row, notes in _gold_rows():
        revision = dict(row["revision"])
        text = notes.get(row["document_id"])
        revision["field_provenance"] = provenance_from_evidence_map(row["evidence"], text)
        result = suggest_codes(revision, source_text=text)
        codes = {c["code"]: c for c in result["codes"]}
        started = {
            p["category"]
            for p in revision["procedures"]
            if p["performance"] in {"performed", "attempted"}
        }
        sampled = {
            s["iaslc_station"]
            for s in revision.get("station_surveys") or []
            if s.get("station_sampled") is True and s.get("survey_modality") != "EUS_B"
        }
        structures = [t for t in revision.get("targets") or [] if t.get("site") == "central_mass"]
        if "linear_ebus" not in started:
            assert not ({"31652", "31653"} & set(codes)), row["document_id"]
        elif not structures:
            if not sampled:
                assert not ({"31652", "31653"} & set(codes)), row["document_id"]
            elif len(sampled) <= 2:
                assert "31652" in codes and "31653" not in codes, row["document_id"]
            else:
                assert "31653" in codes and "31652" not in codes, row["document_id"]
        if "31627" in codes:
            assert revision.get("navigation_runs") and "robotic_bronchoscopy" in started
            assert any(c["role"] == "primary" for c in codes.values())
        lobes = set()
        targets = {t["target_id"]: t for t in revision.get("targets") or []}
        for acquisition in revision.get("sampling_acquisitions") or []:
            target = targets.get(acquisition.get("target_id"))
            if (
                target
                and target.get("site") == "lung"
                and acquisition.get("attribution_status") == "attributed"
                and acquisition.get("sampling_tool") in {"forceps", "mini_forceps", "cryoprobe"}
                and target.get("lobe")
            ):
                lobes.add(target["lobe"])
        assert ("31632" in codes) == (len(lobes) >= 2), row["document_id"]
        if "31632" in codes:
            assert codes["31632"]["units"] == len(lobes) - 1
        for code in codes.values():
            for item in code["evidence"]:
                if "start" in item and text is not None:
                    assert text[item["start"] : item["end"]] == item["quote"]
        checked += 1
    assert checked >= 300


def test_adapter_returns_a_record_and_trace_without_reading_text():
    case = Case(robotic=False)
    case.station("4R", sampled=True)
    record, trace = to_registry_record(case.p)
    assert record.procedures_performed.linear_ebus.performed is True
    assert [e.label for e in trace.facts["nodal"]] == ["Station 4R sampled"]
