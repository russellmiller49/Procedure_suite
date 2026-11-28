"""Full-contract scoring of a proposal against a gold ClinicalRevision.

Rows are aligned by clinical natural keys (lobe or station for targets, station
for surveys, tool and granularity under the aligned target for acquisitions, and
so on); rows that share a key are paired by Hungarian assignment on field
agreement. Per field: a matching value is a true positive, a value where gold has
none is a false fill (FP), a missing value is a miss (FN), and a wrong value is
both. Defaults and "not_documented" count as no value. Parent links are scored
separately as foreign-key accuracy. Wilson lower bounds come with every rate,
because a 98% bar means little at a support of five.
"""

from __future__ import annotations

import math
import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable

from scipy.optimize import linear_sum_assignment

from app.registry_workbench.compare import ID_FIELDS
from app.registry_workbench.extraction.contract_spec import contract_spec
from ip_registry_contracts.launch import ENTITY_MODELS
from ip_registry_contracts.models import ProcedureEvent

STRUCTURAL = ID_FIELDS | {"run_sequence_number", "event_sequence_number", "pass_sequence_number"}
FOREIGN_KEYS = (
    "target_id",
    "station_survey_id",
    "ebus_session_id",
    "navigation_run_id",
    "sampling_pass_id",
    "specimen_id",
)
ALIGN_ORDER = (
    "procedures",
    "targets",
    "ebus_sessions",
    "station_surveys",
    "navigation_runs",
    "localization_events",
    "sampling_acquisitions",
    "specimens",
    "sampling_specimen_links",
    "complications",
    "pathology_results",
    "follow_up",
)
PRIMARY = {
    "targets": "target_id",
    "ebus_sessions": "ebus_session_id",
    "station_surveys": "station_survey_id",
    "navigation_runs": "navigation_run_id",
    "localization_events": "localization_event_id",
    "sampling_acquisitions": "sampling_pass_id",
    "specimens": "specimen_id",
    "sampling_specimen_links": "sampling_specimen_link_id",
    "pathology_results": "pathology_result_id",
}
_KINDS = {
    path: spec.kind
    for path, spec in contract_spec((*ALIGN_ORDER, "case_details", "revision")).fields.items()
}
_DEFAULTS = {
    f"{collection}.{name}": info.default
    for collection, model in {**ENTITY_MODELS, "procedures": ProcedureEvent}.items()
    for name, info in model.model_fields.items()
    if info.default is not None
    and not callable(info.default)
    and isinstance(info.default, (str, bool, int, float))
}
_DEFAULTS["revision.complication_assessment"] = "not_documented"


def _value(collection: str, field: str, value: Any) -> Any:
    if value is None or value == "not_documented":
        return None
    default = _DEFAULTS.get(f"{collection}.{field}")
    if default is not None and str(value) == str(default):
        return None
    return value


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", str(text).lower()))


def _specimen_label_key(label: Any) -> str | None:
    """Alignment key for a specimen label: "Specimen A", "specimen a." and "A" are one specimen.

    A note says "Specimen A"; whether an extractor keeps the word is formatting, not
    content, and must not decide which rows are compared.
    """
    tokens = [t for t in re.findall(r"[a-z0-9]+", str(label or "").lower()) if t != "specimen"]
    return " ".join(tokens) or None


def values_match(collection: str, field: str, a: Any, b: Any) -> bool:
    kind = _KINDS.get(f"{collection}.{field}")
    if kind in {"number", "integer"} or (isinstance(a, (int, float)) and not isinstance(a, bool)):
        try:
            return abs(float(a) - float(b)) < 1e-6
        except (TypeError, ValueError):
            return False
    if kind == "text":
        x, y = _tokens(a), _tokens(b)
        if not x or not y:
            return False
        return x <= y or y <= x or len(x & y) / len(x | y) >= 0.5
    return a == b


@dataclass
class DocumentScore:
    fields: dict[str, list[int]] = field(default_factory=lambda: defaultdict(lambda: [0, 0, 0]))
    rows: dict[str, list[int]] = field(default_factory=lambda: defaultdict(lambda: [0, 0, 0]))
    foreign_keys: list[int] = field(default_factory=lambda: [0, 0])


def _keys(values: dict[str, Any]) -> dict[str, Callable[[dict], Any]]:
    by_id: dict[str, dict[str, dict]] = {
        collection: {row.get(pk): row for row in values.get(collection) or [] if row.get(pk)}
        for collection, pk in PRIMARY.items()
    }

    def target(row: dict) -> Any:
        t = by_id["targets"].get(row.get("target_id"))
        if t is None:
            return None
        if t.get("site") == "lymph_node":
            return ("node", t.get("iaslc_station"))
        if t.get("site") == "central_mass":
            return ("central", t.get("anatomic_label"))
        return ("lung", t.get("lobe"))

    def acquisition(row: dict) -> Any:
        return (target(row), row.get("sampling_tool"), row.get("acquisition_record_granularity"))

    def specimen(row: dict) -> Any:
        return _specimen_label_key(row.get("specimen_label")) or (
            target(row),
            row.get("specimen_type"),
        )

    return {
        "procedures": lambda r: r.get("category"),
        "targets": lambda r: (
            target({"target_id": r.get("target_id")})
            if r.get("target_id")
            else ("lung", r.get("lobe"))
        ),
        "ebus_sessions": lambda r: "session",
        "station_surveys": lambda r: r.get("iaslc_station"),
        "navigation_runs": target,
        "localization_events": lambda r: (target(r), r.get("localization_modality")),
        "sampling_acquisitions": acquisition,
        "specimens": specimen,
        "sampling_specimen_links": lambda r: (
            acquisition(by_id["sampling_acquisitions"].get(r.get("sampling_pass_id"), {})),
            specimen(by_id["specimens"].get(r.get("specimen_id"), {})),
        ),
        "complications": lambda r: r.get("category"),
        "pathology_results": lambda r: (
            specimen(by_id["specimens"].get(r.get("specimen_id"), {})),
            r.get("result_status"),
        ),
        "follow_up": lambda r: r.get("window"),
    }


def _scored(collection: str, row: dict) -> dict[str, Any]:
    scored = {
        name: v
        for name, raw in row.items()
        if name not in STRUCTURAL and (v := _value(collection, name, raw)) is not None
    }
    # A single-pass row represents one pass whether or not the count is written out: the
    # contract accepts only none or 1 there, and the dictionary defines it as one.
    if (
        collection == "sampling_acquisitions"
        and row.get("acquisition_record_granularity") == "single_pass"
        and scored.get("reported_pass_count") == 1
    ):
        del scored["reported_pass_count"]
    return scored


def _agreement(collection: str, a: dict, b: dict) -> int:
    return sum(1 for k, v in a.items() if k in b and values_match(collection, k, v, b[k]))


def _align(
    collection: str, gold_rows: list[dict], pred_rows: list[dict], gold_key, pred_key
) -> list[tuple[int | None, int | None]]:
    groups: dict[Any, tuple[list[int], list[int]]] = defaultdict(lambda: ([], []))
    for i, row in enumerate(gold_rows):
        groups[repr(gold_key(row))][0].append(i)
    for j, row in enumerate(pred_rows):
        groups[repr(pred_key(row))][1].append(j)
    pairs: list[tuple[int | None, int | None]] = []
    for gold_ids, pred_ids in groups.values():
        if gold_ids and pred_ids:
            scores = [
                [
                    _agreement(
                        collection,
                        _scored(collection, gold_rows[i]),
                        _scored(collection, pred_rows[j]),
                    )
                    for j in pred_ids
                ]
                for i in gold_ids
            ]
            rows, cols = linear_sum_assignment([[-s for s in line] for line in scores])
            matched_g, matched_p = set(), set()
            for r, c in zip(rows, cols, strict=True):
                pairs.append((gold_ids[r], pred_ids[c]))
                matched_g.add(gold_ids[r])
                matched_p.add(pred_ids[c])
            pairs += [(i, None) for i in gold_ids if i not in matched_g]
            pairs += [(None, j) for j in pred_ids if j not in matched_p]
        else:
            pairs += [(i, None) for i in gold_ids] + [(None, j) for j in pred_ids]
    return pairs


def _compare_fields(score: DocumentScore, collection: str, gold: dict, pred: dict) -> None:
    g, p = _scored(collection, gold), _scored(collection, pred)
    for name in set(g) | set(p):
        counts = score.fields[f"{collection}.{name}"]
        if name in g and name in p:
            if values_match(collection, name, g[name], p[name]):
                counts[0] += 1
            else:
                counts[1] += 1
                counts[2] += 1
        elif name in p:
            counts[1] += 1
        else:
            counts[2] += 1


def score_document(gold: dict[str, Any], predicted: dict[str, Any] | None) -> DocumentScore:
    predicted = predicted or {}
    score = DocumentScore()
    _compare_fields(
        score, "case_details", gold.get("case_details") or {}, predicted.get("case_details") or {}
    )
    _compare_fields(
        score,
        "revision",
        {"complication_assessment": gold.get("complication_assessment")},
        {"complication_assessment": predicted.get("complication_assessment")},
    )
    gold_keys, pred_keys = _keys(gold), _keys(predicted)
    id_map: dict[str, str] = {}
    matched: list[tuple[str, dict, dict]] = []
    for collection in ALIGN_ORDER:
        gold_rows, pred_rows = gold.get(collection) or [], predicted.get(collection) or []
        pairs = _align(
            collection, gold_rows, pred_rows, gold_keys[collection], pred_keys[collection]
        )
        rows = score.rows[collection]
        for i, j in pairs:
            if i is not None and j is not None:
                rows[0] += 1
                g, p = gold_rows[i], pred_rows[j]
                _compare_fields(score, collection, g, p)
                if collection in PRIMARY and g.get(PRIMARY[collection]):
                    id_map[g[PRIMARY[collection]]] = p.get(PRIMARY[collection])
                matched.append((collection, g, p))
            elif i is not None:
                rows[2] += 1
                _compare_fields(score, collection, gold_rows[i], {})
            else:
                rows[1] += 1
                _compare_fields(score, collection, {}, pred_rows[j])
    # Links are checked once every collection is aligned (targets point at later surveys).
    for collection, g, p in matched:
        for fk in FOREIGN_KEYS:
            if fk != PRIMARY.get(collection) and g.get(fk):
                score.foreign_keys[1] += 1
                score.foreign_keys[0] += int(
                    p.get(fk) is not None and id_map.get(g[fk]) == p.get(fk)
                )
    return score


def wilson_lower(successes: int, total: int, z: float = 1.96) -> float | None:
    if total == 0:
        return None
    p = successes / total
    centre = p + z * z / (2 * total)
    margin = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total))
    return (centre - margin) / (1 + z * z / total)


def rates(tp: int, fp: int, fn: int, *, min_support: int = 20) -> dict[str, Any]:
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    f1 = 2 * precision * recall / (precision + recall) if precision and recall else None
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "support": tp + fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "precision_lower": wilson_lower(tp, tp + fp),
        "recall_lower": wilson_lower(tp, tp + fn),
        "sufficient_support": tp + fn >= min_support,
    }


def aggregate(scores: list[DocumentScore], *, min_support: int = 20) -> dict[str, Any]:
    fields: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0])
    rows: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0])
    fk = [0, 0]
    for s in scores:
        for k, v in s.fields.items():
            fields[k] = [a + b for a, b in zip(fields[k], v, strict=True)]
        for k, v in s.rows.items():
            rows[k] = [a + b for a, b in zip(rows[k], v, strict=True)]
        fk = [fk[0] + s.foreign_keys[0], fk[1] + s.foreign_keys[1]]
    by_entity: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0])
    for k, v in fields.items():
        by_entity[k.split(".")[0]] = [
            a + b for a, b in zip(by_entity[k.split(".")[0]], v, strict=True)
        ]
    total = [sum(v[i] for v in fields.values()) for i in range(3)]
    return {
        "documents": len(scores),
        "overall": rates(*total, min_support=min_support),
        "entities": {k: rates(*v, min_support=min_support) for k, v in sorted(by_entity.items())},
        "fields": {k: rates(*v, min_support=min_support) for k, v in sorted(fields.items())},
        "rows": {k: rates(*v, min_support=min_support) for k, v in sorted(rows.items())},
        "foreign_key_accuracy": {
            "correct": fk[0],
            "total": fk[1],
            "rate": fk[0] / fk[1] if fk[1] else None,
            "lower": wilson_lower(fk[0], fk[1]),
        },
    }


__all__ = ["DocumentScore", "aggregate", "rates", "score_document", "values_match", "wilson_lower"]
