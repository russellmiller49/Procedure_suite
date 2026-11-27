"""Versioned, unadjusted launch counts. No staging sensitivity or later-truth yield.

    https://pubmed.ncbi.nlm.nih.gov/38394646/
Counts remain unsuppressed here; national callers must apply their disclosure policy.
"""

from collections import Counter
from .launch import PROFILE, VERSION
from .models import eligibility


def attempted_targets(record):
    started = {n.target_id for n in record.navigation_runs} | {
        e.target_id for e in record.localization_events
    }
    started |= {a.target_id for a in record.sampling_acquisitions if a.target_id is not None}
    robotic = any(
        str(p.category) == "robotic_bronchoscopy"
        and str(p.performance) in {"attempted", "performed"}
        for p in record.procedures
    )
    return [
        t
        for t in record.targets
        if robotic
        and t.site == "lung"
        and t.prespecified_biopsy_target is True
        and (t.diagnostic_attempted is True or t.target_id in started)
    ]


def target_index_result(record, target_id):
    specimens = {
        s.specimen_id
        for s in record.specimens
        if s.target_id == target_id and s.target_attribution_status == "attributed"
    }
    superseded = {
        p.supersedes_pathology_result_id
        for p in record.pathology_results
        if p.supersedes_pathology_result_id
    }
    results = [
        p
        for p in record.pathology_results
        if p.specimen_id in specimens
        and p.target_id == target_id
        and p.result_scope == "index"
        and p.pathology_result_id not in superseded
    ]
    classes = {p.index_result_class for p in results if p.result_status in {"final", "amended"}}
    specific = classes & {"specific_malignant", "specific_benign"}
    if len(specific) > 1:
        return "conflicting_results"
    if specific:
        return next(iter(specific))
    if not results or any(p.result_status in {"pending", "preliminary"} for p in results):
        return "pending_or_unassessed"
    for category in ("atypical_or_suspicious", "nonspecific_benign", "nondiagnostic"):
        if category in classes:
            return category
    return "pending_or_unassessed"


def launch_measures(records):
    records = list(records)
    counts = Counter(
        {
            key: 0
            for key in (
                "cases_received",
                "cases_started",
                "cases_completed",
                "cases_aborted",
                "cases_partially_completed",
                "cases_completion_unknown",
                "cases_eligibility_review",
                "robotic_cases_started",
                "linear_ebus_cases_started",
                "peripheral_targets_attempted",
                "targets_eligibility_unassessed",
                "targets_with_specimen",
                "targets_without_specimen",
                "targets_specimen_unassessed",
                "specimens_attribution_review",
                "navigation_reached",
                "navigation_failed",
                "navigation_unassessed",
                "acquisition_records",
                "aggregate_acquisition_records",
                "reported_passes",
                "acquisitions_count_unreported",
                "nodal_targets_sampled",
                "nodal_targets_adequate",
                "nodal_targets_inadequate",
                "nodal_adequacy_unassessed",
                "index_specific_malignant",
                "index_specific_benign",
                "index_atypical_or_suspicious",
                "index_nonspecific_benign",
                "index_nondiagnostic",
                "index_pending_or_unassessed",
                "index_conflicting_results",
                "strict_index_diagnostic_results",
                "later_followup_results",
                "safety_immediate_present",
                "safety_immediate_absent",
                "safety_immediate_unassessed",
                "safety_30_day_assessed",
                "safety_30_day_incomplete",
                "safety_30_day_events",
                "safety_30_day_no_events",
                "safety_30_day_outcome_unassessed",
            )
        }
    )
    for window in ("days_0_7", "days_8_30"):
        for field in (
            "ed_visit",
            "unplanned_admission",
            "icu_admission",
            "unplanned_ventilation",
            "alive",
        ):
            for value in ("present", "absent", "unassessed"):
                counts[f"{window}_{field}_{value}"] = 0
    counts["cases_received"] = len(records)
    for record in records:
        if eligibility(record) != "eligible":
            counts["cases_eligibility_review"] += 1
            continue
        counts["cases_started"] += 1
        started = [p for p in record.procedures if str(p.performance) in {"attempted", "performed"}]
        counts["robotic_cases_started"] += any(
            str(p.category) == "robotic_bronchoscopy" for p in started
        )
        counts["linear_ebus_cases_started"] += any(
            str(p.category) == "linear_ebus" for p in started
        )
        if all(p.completion == "completed" for p in started):
            counts["cases_completed"] += 1
        elif any(p.completion == "aborted_after_start" for p in started):
            counts["cases_aborted"] += 1
        elif any(p.completion == "partially_completed" for p in started):
            counts["cases_partially_completed"] += 1
        else:
            counts["cases_completion_unknown"] += 1
        targets = attempted_targets(record)
        counts["peripheral_targets_attempted"] += len(targets)
        attempted_ids = {t.target_id for t in targets}
        counts["targets_eligibility_unassessed"] += sum(
            t.site == "lung"
            and (
                t.prespecified_biopsy_target is None
                or (
                    t.prespecified_biopsy_target is True
                    and t.diagnostic_attempted is None
                    and t.target_id not in attempted_ids
                )
            )
            for t in record.targets
        )
        for target in targets:
            result = target_index_result(record, target.target_id)
            counts["index_" + result] += 1
            counts["strict_index_diagnostic_results"] += result in {
                "specific_malignant",
                "specific_benign",
            }
            counts[
                {
                    True: "targets_with_specimen",
                    False: "targets_without_specimen",
                    None: "targets_specimen_unassessed",
                }[target.specimen_obtained]
            ] += 1
        counts["specimens_attribution_review"] += sum(
            s.target_attribution_status != "attributed" for s in record.specimens
        )
        for nav in record.navigation_runs:
            counts[
                {
                    True: "navigation_reached",
                    False: "navigation_failed",
                    None: "navigation_unassessed",
                }[nav.target_reached_operational]
            ] += 1
        counts["acquisition_records"] += len(record.sampling_acquisitions)
        for acq in record.sampling_acquisitions:
            counts["aggregate_acquisition_records"] += (
                acq.acquisition_record_granularity == "aggregate_reported"
            )
            if acq.reported_pass_count is None:
                counts["acquisitions_count_unreported"] += 1
            else:
                counts["reported_passes"] += acq.reported_pass_count
        for target in record.targets:
            if target.site == "lymph_node" and target.sampling_attempted is True:
                counts["nodal_targets_sampled"] += 1
                counts[
                    {
                        True: "nodal_targets_adequate",
                        False: "nodal_targets_inadequate",
                        None: "nodal_adequacy_unassessed",
                    }[target.target_specimen_adequate]
                ] += 1
        counts["later_followup_results"] += sum(
            p.result_scope == "followup" for p in record.pathology_results
        )
        present_events = [c for c in record.complications if str(c.state) == "present"]
        state = (
            "present"
            if any(c.event_time_window == "immediate" for c in present_events)
            else str(record.complication_assessment)
        )
        counts[
            "safety_immediate_" + (state if state in {"present", "absent"} else "unassessed")
        ] += 1
        windows = {f.window: f for f in record.follow_up}
        complete = len(windows) == 2 and all(f.complete for f in windows.values())
        counts["safety_30_day_assessed" if complete else "safety_30_day_incomplete"] += 1
        outcomes = {str(f.procedure_related_event) for f in windows.values()}
        if any(
            c.relatedness_to_procedure == "related"
            and (
                c.event_time_window in {"immediate", "days_0_7", "days_8_30"}
                or c.relative_day_offset is not None
            )
            for c in present_events
        ):
            outcomes.add("present")
        outcome = (
            "events"
            if "present" in outcomes
            else ("no_events" if complete and outcomes == {"absent"} else "outcome_unassessed")
        )
        counts["safety_30_day_" + outcome] += 1
        for window in ("days_0_7", "days_8_30"):
            row = windows.get(window)
            for field in (
                "ed_visit",
                "unplanned_admission",
                "icu_admission",
                "unplanned_ventilation",
                "alive",
            ):
                value = str(getattr(row, field)) if row else "not_documented"
                counts[
                    f"{window}_{field}_"
                    + (value if value in {"present", "absent"} else "unassessed")
                ] += 1
    denominator = counts["peripheral_targets_attempted"]
    return {
        "version": VERSION,
        "registry_profile": PROFILE,
        "adjustment": "unadjusted",
        "counts": dict(counts),
        "strict_index_yield": {
            "numerator": counts["strict_index_diagnostic_results"],
            "denominator": denominator,
            "rate": counts["strict_index_diagnostic_results"] / denominator
            if denominator
            else None,
        },
        "definitions": {
            "peripheral_attempt": "navigation, localization or sampling started for a prespecified biopsy target; failures included",
            "strict_index_yield": "specific diagnosis from final/amended index specimens attributed to the same target",
            "missingness": "pending and unassessed reported explicitly",
            "validation": "engineering; not clinical validation",
        },
    }
