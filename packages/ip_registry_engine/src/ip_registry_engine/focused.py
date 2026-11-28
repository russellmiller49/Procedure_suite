"""Bounded, evidence-bearing robotic/linear-EBUS proposals for local review.

The broad development pipeline remains independent. This extractor never assigns
source-free outcomes or applies proposals to an approved revision.
"""

import hashlib
import re
from uuid import UUID
from ip_registry_contracts.launch import ENTITY_MODELS, VERSION

PHASES = (
    "source_preparation",
    "deterministic_uplift",
    "narrative_reconciliation",
    "precision_guardrails",
    "evidence_verification",
    "launch_projection",
    "omission_audit",
)
STATION = r"(?:11Rs|11Ri|(?:2|4|10|11|12)[RL]|3[AP]|[5-9])"
LOBE = r"\b(?:RUL|RML|RLL|LUL|LLL|Lingula|right upper lobe|right middle lobe|right lower lobe|left upper lobe|left lower lobe)\b"
LOBE_MAP = {
    "right upper lobe": "RUL",
    "right middle lobe": "RML",
    "right lower lobe": "RLL",
    "left upper lobe": "LUL",
    "left lower lobe": "LLL",
    "lingula": "Lingula",
}
ACTION = r"(?:perform\w*|introduc\w*|advanc\w*|navigat\w*|navagat\w*|navgat\w*|sample\w*|sampl\w*|reached|dock\w*|attempt\w*|aborted|biops\w*|biosp\w*|completed|(?:was|were) used)"
NEGATIVE = re.compile(
    r"\b(?:not (?:performed|used|attempted|started)|never started|cancelled before|no (?:linear |convex |CP-)?EBUS|planned only|scheduled for|history of|prior procedure)\b",
    re.I,
)
MODALITIES = (
    ("fixed_CBCT", r"\bfixed(?:[- ]room)?\s+(?:cone[- ]beam\s*CT|CBCT)"),
    ("mobile_CBCT", r"\b(?:mobile(?: C[- ]arm)?\s+(?:cone[- ]beam\s*CT|CBCT)|mCBCT)\b"),
    ("CBCT_unspecified", r"\b(?:cone[- ]beam\s*CT|CBCT)\b"),
    (
        "digital_tomosynthesis",
        r"\b(?:digital tomos[yi]nthesis|digital tomosythesis|DT (?:sweep|was|suggested))\b",
    ),
    ("radial_EBUS", r"\b(?:radial[- ](?:probe[- ]?)?(?:EBUS|US|ultraso\w*|probe)|rEBUS)\b"),
    ("augmented_fluoroscopy", r"\baugmented fluoroscop\w*"),
    ("2D_fluoroscopy", r"\bfluoroscop(?:y|ic guidance)\b"),
)


def stable_id(digest, key):
    # UUID4-compatible deterministic pseudorandom proposal IDs permit job replay.
    return str(UUID(bytes=hashlib.sha256((digest + ":" + key).encode()).digest()[:16], version=4))


def prepare_text(text):
    chars = list(text)
    for match in re.finditer(
        r"(?im)^.*(?:synthetic downstream pathology label|hidden (?:final|outcome)|dataset (?:label|outcome)|^\s*(?:HISTORY|PLAN|SCHEDULED|PROCEDURE CODES)\s*:|^\s*\d{5}\s).*$",
        text,
    ):
        chars[match.start() : match.end()] = " " * (match.end() - match.start())
    # Recover soft PDF line wraps without shifting source spans or joining headings.
    for match in re.finditer(r"\n", text):
        previous = text[text.rfind("\n", 0, match.start()) + 1 : match.start()].strip()
        following = text[match.end() :]
        if (
            previous
            and not previous.isupper()
            and not following.split("\n", 1)[0].strip().isupper()
            and re.search(r"[\w,)]$", previous)
            and re.match(
                r"(?:[a-z]|(?:EBUS|CBCT|TBNA|ROSE)\b|\(\d+(?:\.\d+)?\s*mm\)|" + STATION + r"\s*\()",
                following,
            )
            and chars[match.start() - 1] != " "
        ):
            chars[match.start()] = " "
    return "".join(chars)


def segments(text):
    # Decimal points are measurements, not sentence boundaries. Keep offsets into
    # the original document so normalized centimetres retain their exact evidence.
    result, start = [], 0
    for boundary in re.finditer(r"[\n;|]|(?<!\d)\.|\.(?!\d)", text):
        end = boundary.end()
        if text[start:end].strip():
            result.append((start, end, text[start:end]))
        start = end
    if text[start:].strip():
        result.append((start, len(text), text[start:]))
    return result


def extract_procedure(request, ner_spans=()):
    text = request.text
    masked = prepare_text(text)
    parts = segments(masked)
    summary_spans = []
    for match in re.finditer(
        r"(?im)^[ \t]*(?:\*\*)?(?:final )?impression(?:\*\*)?\s*:?[ \t]*", masked
    ):
        following = re.search(
            r"(?im)^[ \t]*(?:\*\*)?(?:details|findings|procedure in detail|imaging confirmation|robotic navigation)\b",
            masked[match.end() :],
        )
        summary_spans.append(
            (match.start(), match.end() + following.start() if following else len(masked))
        )
    proposal = {
        "schema_version": VERSION,
        "registry_profile": "robotic_ebus_v1",
        "procedures": [],
        **{key: {} if key == "case_details" else [] for key in ENTITY_MODELS},
        "field_provenance": [],
    }
    warnings, unresolved = [], []
    provenance = {}

    def has_action(part):
        return bool(re.search(ACTION, part[2], re.I)) or any(
            span["label"].endswith("-PROC_ACTION")
            and part[0] <= span["start"] < span["end"] <= part[1]
            for span in ner_spans
        )

    def set_value(path, value, span, *, derived=False):
        node = proposal
        keys = path.strip("/").split("/")
        for key in keys[:-1]:
            node = node[int(key)] if isinstance(node, list) else node[key]
        node[keys[-1]] = value
        start, end = span
        provenance[path] = {
            "field_path": path,
            "source_document_id": str(request.source_document_id),
            "source_digest": request.source_digest,
            "source_start": start,
            "source_end": end,
            "source_excerpt": text[start:end],
            "raw_value": text[start:end],
            "value_origin": "derived" if derived else "extracted",
            "extractor_model_version": VERSION,
            "derivation_rule_version": VERSION if derived else None,
            "assertion_context": "active",
            "conflict_status": provenance.get(path, {}).get("conflict_status", "none"),
        }

    def put(collection, row, span):
        index = len(proposal[collection])
        proposal[collection].append({})
        for key, value in row.items():
            if value is not None:
                set_value(f"/{collection}/{index}/{key}", value, span, derived=key.endswith("_id"))
        return index

    platform = re.search(r"\b(Ion|Monarch|Galaxy)\b", masked, re.I)
    robotic = re.search(r"\brobot(?:ic|iic|c)?(?:[- ]assisted)?\b", masked, re.I)
    # Action must appear in narrative, not only in a platform/header list.
    robotic_action = next(
        (
            p
            for p in parts
            if has_action(p)
            and not NEGATIVE.search(p[2])
            and (
                re.search(
                    r"robot|catheter|bronchoscope|navigation|navagation|target.*reached", p[2], re.I
                )
            )
        ),
        None,
    )
    therapy_only = bool(re.search(r"\b(?:ablation|therapeutic)\b", masked, re.I)) and not re.search(
        r"\b(?:biopsy|biopsies|sampling|tissue diagnosis)\b", masked, re.I
    )
    platform_action = next(
        (
            p
            for p in parts
            if platform
            and re.search(r"\b" + platform.group() + r"\b", p[2], re.I)
            and not NEGATIVE.search(p[2])
            and re.search(
                r"(?:docked|registered|guided|navigated|advanced|used to (?:register|guide|navigate))",
                p[2],
                re.I,
            )
            and re.search(r"catheter|platform|system|bronchoscopy", p[2], re.I)
        ),
        None,
    )
    if (robotic and robotic_action or platform_action) and not therapy_only:
        robotic_action = robotic_action if robotic else platform_action
        failure = next(
            (
                p
                for p in parts
                if re.search(
                    r"(?:navigation|robot\w*|procedure|attempt).{0,55}(?:failed|aborted|unsuccessful)|unable to (?:reach|navigate)",
                    p[2],
                    re.I,
                )
                and not NEGATIVE.search(p[2])
            ),
            None,
        )
        completed = next(
            (
                p
                for p in parts
                if re.search(
                    r"(?:procedure|robotic\w*|bronchoscopy).{0,40}completed|successful.{0,35}robot|successful.{0,20}(?:Ion|Monarch|Galaxy)",
                    p[2],
                    re.I,
                )
            ),
            None,
        )
        row = {
            "category": "robotic_bronchoscopy",
            "performance": "attempted" if failure else "performed",
            "completion": "aborted_after_start" if failure else "completed" if completed else None,
            "abort_reason": failure[2].strip() if failure else None,
        }
        put("procedures", row, robotic_action[:2])
    ebus_pattern = (
        r"\b(?:linear\s+EBUS|convex(?:[- ]probe)?\s+EBUS|CP[- ]EBUS|EBUS[- ]TBNA|EBUS TBNA)\b"
    )
    ebus_parts = [p for p in parts if re.search(ebus_pattern, p[2], re.I)]
    positive = next((p for p in ebus_parts if not NEGATIVE.search(p[2]) and has_action(p)), None)
    if positive is None and ebus_parts and not any(NEGATIVE.search(p[2]) for p in ebus_parts):
        # A named EBUS staging section with explicit station needle sampling is
        # action-target evidence even when its heading has no finite action verb.
        section = re.search(
            r"(?im)^[ \t]*(?:\*\*)?EBUS(?:[- ](?:STAGING|SAMPLING|PROCEDURE)\b|[ \t]*(?:\*\*)?:?[ \t]*$)",
            masked,
        )
        station_action = next(
            (
                p
                for p in parts
                if section
                and p[0] >= section.end()
                and re.search(r"\b(?:station|stn|staion)\s+(?:level\s+)?" + STATION, p[2], re.I)
                and re.search(r"\b\d+\s+(?:needle )?passes\b", p[2], re.I)
                and not re.search(r"not sampled|not performed|EUS[- ]B", p[2], re.I)
            ),
            None,
        )
        if section and station_action and not re.search(r"EUS[- ]B", masked, re.I):
            if station_action[1] - section.start() <= 4096:
                positive = (
                    section.start(),
                    station_action[1],
                    masked[section.start() : station_action[1]],
                )
    if positive:
        # EUS-B-only text does not establish a transbronchial linear EBUS component.
        if not re.search(r"EUS[- ]B[- ]only|exclusively transesophageal", masked, re.I):
            aborted = bool(re.search(r"aborted|unable to|failed", positive[2], re.I))
            put(
                "procedures",
                {
                    "category": "linear_ebus",
                    "performance": "attempted" if aborted else "performed",
                    "completion": "aborted_after_start" if aborted else None,
                },
                positive[:2],
            )
    elif ebus_parts and proposal["procedures"] and any(NEGATIVE.search(p[2]) for p in ebus_parts):
        denied = next(p for p in ebus_parts if NEGATIVE.search(p[2]))
        put(
            "procedures",
            {
                "category": "linear_ebus",
                "performance": "not_performed",
                "completion": "not_started",
            },
            denied[:2],
        )
    if not any(p["performance"] in {"performed", "attempted"} for p in proposal["procedures"]):
        uncertain = (robotic is not None and not therapy_only) or any(
            not NEGATIVE.search(p[2]) for p in ebus_parts
        )
        if uncertain:
            category = "robotic_bronchoscopy" if robotic is not None else "linear_ebus"
            mention = robotic.span() if robotic is not None else ebus_parts[0][:2]
            put("procedures", {"category": category, "performance": "unknown"}, mention)
            proposal["field_provenance"] = list(provenance.values())
        return {
            "proposal": proposal,
            "quality_signals": [{"phase": p, "status": "completed"} for p in PHASES],
            "unresolved_mentions": [],
            "ner_spans": list(ner_spans),
        }, ["eligibility_requires_review" if uncertain else "outside_launch_scope"]

    for field, pattern, transform in (
        ("age_at_procedure_years", r"\b(\d{1,3})[- ]year[- ]old\b", float),
        (
            "sex_at_birth",
            r"\b(male|female|man|woman)\b",
            lambda v: {"man": "male", "woman": "female"}.get(v.lower(), v.lower()),
        ),
        ("asa_physical_status", r"\bASA\s*(?:class\s*)?([1-6])\b", int),
        ("pack_years", r"\b(\d+(?:\.\d+)?)\s*pack[- ]year", float),
        ("airway_size_value", r"\b(\d+(?:\.\d+)?)[- ]mm\s+(?:endotracheal tube|ETT)", float),
        (
            "procedure_duration_minutes",
            r"\b(?:procedure duration|procedure time)\s*:?\s*(\d+(?:\.\d+)?)\s*min",
            float,
        ),
    ):
        match = re.search(pattern, masked, re.I)
        if match:
            set_value("/case_details/" + field, transform(match.group(1)), match.span())
            if field == "airway_size_value":
                set_value("/case_details/airway_size_unit", "mm", match.span())
    for field, value, pattern in (
        ("anesthesia_type", "general", r"\b(?:general an\w*esia|GA)\b"),
        ("anesthesia_type", "moderate", r"\bmoderate sedation\b"),
        ("airway_device", "ETT", r"\b(?:endotracheal (?:tube|intubation)|ETT)\b"),
        ("airway_device", "LMA", r"\b(?:laryngeal mask airway|LMA|supraglottic airway)\b"),
    ):
        match = re.search(pattern, masked, re.I)
        if match:
            set_value("/case_details/" + field, value, match.span())

    lung_targets = []
    if any(p["category"] == "robotic_bronchoscopy" for p in proposal["procedures"]):
        lobes = {}
        for p in parts:
            if not re.search(r"lesion|lesoin|nod\w*|target|opacity|\bmass\b", p[2], re.I):
                continue
            for m in re.finditer(LOBE, p[2], re.I):
                lobe = LOBE_MAP.get(m.group().lower(), m.group().upper())
                lobes.setdefault(lobe, p)
        for lobe, part in lobes.items():
            target_id = stable_id(request.source_digest, "lung:" + lobe)
            index = put(
                "targets",
                {
                    "target_id": target_id,
                    "site": "lung",
                    "lobe": lobe,
                    "prespecified_biopsy_target": True
                    if re.search(r"target|planned|preprocedure", part[2], re.I)
                    else None,
                },
                part[:2],
            )
            lung_targets.append((target_id, index))
            size = re.search(r"\b(\d+(?:\.\d+)?)[- ]?(mm|cm)\b", part[2], re.I)
            if size:
                set_value(
                    f"/targets/{index}/max_diameter_mm",
                    round(float(size.group(1)) * (10 if size.group(2).lower() == "cm" else 1), 6),
                    (part[0] + size.start(), part[0] + size.end()),
                    derived=size.group(2).lower() == "cm",
                )
            density = re.search(
                r"\b(part[- ]solid|ground[- ]glass|solid|cavitary)\b", part[2], re.I
            )
            if density:
                set_value(
                    f"/targets/{index}/lesion_attenuation_type",
                    density.group().lower().replace("-", "_").replace(" ", "_"),
                    (part[0] + density.start(), part[0] + density.end()),
                )
            seg = re.search(r"\b([RL]B\d+(?:\+\d+)?)\b", part[2], re.I)
            if seg:
                set_value(
                    f"/targets/{index}/segment",
                    seg.group().upper(),
                    (part[0] + seg.start(), part[0] + seg.end()),
                )
        if len(lung_targets) > 1 or re.search(
            r"\b(?:two|three|multiple|2|3)\s+(?:lesions|nodules|targets)\b", masked, re.I
        ):
            warnings.append("unresolved_target_attribution")
            unresolved.append(
                {
                    "kind": "multiple_peripheral_targets",
                    "reason": "confirm_individual_target_identity_and_attribute_events",
                }
            )
            # A lobe mention does not identify which lesion within that lobe was attempted.
            for _, index in lung_targets:
                for field in ("prespecified_biopsy_target", "diagnostic_attempted"):
                    proposal["targets"][index].pop(field, None)
                    provenance.pop(f"/targets/{index}/{field}", None)

    if len(lung_targets) == 1 and "unresolved_target_attribution" not in warnings:
        target_id, target_index = lung_targets[0]
        navigation_action = next(
            (
                p
                for p in parts
                if not NEGATIVE.search(p[2])
                and re.search(
                    r"navigat\w*|navagat\w*|navgat\w*|target.{0,80}(?:was reached|were reached)|reached the target|catheter was advanced",
                    p[2],
                    re.I,
                )
            ),
            None,
        )
        nav_id = stable_id(request.source_digest, "navigation:0") if navigation_action else None
        nav_row = {
            "navigation_run_id": nav_id,
            "target_id": target_id,
            "run_sequence_number": 1,
            "platform_family": platform.group().capitalize() if platform else None,
        }
        if navigation_action:
            put("navigation_runs", nav_row, navigation_action[:2])
            set_value(f"/targets/{target_index}/diagnostic_attempted", True, navigation_action[:2])
        for p in parts:
            if nav_id and re.search(
                r"(?:target|lesion|planned).{0,80}(?:was reached|were reached)|reached the target",
                p[2],
                re.I,
            ):
                set_value("/navigation_runs/0/target_reached_operational", True, p[:2])
            elif nav_id and re.search(
                r"unable to reach|target.{0,25}not reached|navigation failed", p[2], re.I
            ):
                set_value("/navigation_runs/0/target_reached_operational", False, p[:2])
                set_value("/navigation_runs/0/navigation_failure_reason", p[2].strip(), p[:2])
            match = re.search(
                r"bronchus sign\s*(?:was |is )?(present|positive|absent|negative)", p[2], re.I
            )
            if match:
                set_value(
                    f"/targets/{target_index}/bronchus_sign_present",
                    match.group(1).lower() in {"present", "positive"},
                    p[:2],
                )
            match = re.search(
                r"(?:pleural distance.{0,20}?|located (?:about|approximately) )(\d+(?:\.\d+)?)\s*mm",
                p[2],
                re.I,
            )
            if match:
                set_value(
                    f"/targets/{target_index}/distance_to_pleura_mm", float(match.group(1)), p[:2]
                )
        sequence = 0
        for start, end, sentence in parts:
            if any(a <= start < b for a, b in summary_spans):
                continue
            if re.match(r"\s*(?:\*\*)?procedures? performed(?:\*\*)?\s*:", sentence, re.I):
                continue
            if NEGATIVE.search(sentence) or re.search(
                r"\bno (?:CBCT|rEBUS|radial)", sentence, re.I
            ):
                continue
            matches = [(name, re.search(pattern, sentence, re.I)) for name, pattern in MODALITIES]
            matches = [(name, m) for name, m in matches if m]
            if any(name in {"fixed_CBCT", "mobile_CBCT"} for name, _ in matches):
                matches = [(name, m) for name, m in matches if name != "CBCT_unspecified"]
            if any(name == "augmented_fluoroscopy" for name, _ in matches):
                matches = [(name, m) for name, m in matches if name != "2D_fluoroscopy"]
            if not re.search(
                r"obtained|performed|show\w*|demonstrat\w*|confirm(?:ed|s|ing)\b|used|provided|suggested|localized|(?:rEBUS|radial.{0,15}EBUS)\s*:\s*(?:concent(?:ric|irc)\w*|eccentr\w*)|\bDT\b.{0,25}(?:close|eccentric|off.center)",
                sentence,
                re.I,
            ):
                continue
            for modality, _ in sorted(matches, key=lambda item: item[1].start()):
                sequence += 1
                row = {
                    "localization_event_id": stable_id(
                        request.source_digest, f"localization:{sequence}"
                    ),
                    "target_id": target_id,
                    "navigation_run_id": nav_id,
                    "event_sequence_number": sequence,
                    "localization_modality": modality,
                }
                if modality == "radial_EBUS":
                    for pattern, value in (
                        (r"\bconcent(?:ric|irc)\b", "concentric"),
                        (r"\beccentric\b", "eccentric"),
                        (r"not.{0,20}visual|no discrete", "not_visualized"),
                    ):
                        if re.search(pattern, sentence, re.I):
                            row["radial_ebus_view"] = value
                if (
                    re.search(
                        r"(?:sampling|biopsy) tool|needle tip|forceps|cryoprobe", sentence, re.I
                    )
                    and re.search(
                        r"within (?:the |actual )?lesion|through the lesion|tool[- ]in[- ]lesion",
                        sentence,
                        re.I,
                    )
                    and not re.search(
                        r"suggested|virtual|not confirm|uncertain|without", sentence, re.I
                    )
                    and modality
                    in {"fixed_CBCT", "mobile_CBCT", "CBCT_unspecified", "digital_tomosynthesis"}
                ):
                    row.update(
                        tool_lesion_relationship="TIL",
                        sampling_tool_present=True,
                        lesion_visible=True,
                        actual_lesion_vs_virtual_target="actual_lesion",
                        verified_tool_component="sampling_tool",
                        confirmation_basis="tomosynthesis"
                        if modality == "digital_tomosynthesis"
                        else "volumetric_imaging",
                    )
                put("localization_events", row, (start, end))
                set_value(f"/targets/{target_index}/diagnostic_attempted", True, (start, end))
            if (
                re.search(
                    r"(?:catheter|tool).{0,40}(?:reposition|redirect|changed|adjusted)",
                    sentence,
                    re.I,
                )
                and proposal["localization_events"]
            ):
                event_index = len(proposal["localization_events"]) - 1
                set_value(
                    f"/localization_events/{event_index}/catheter_or_tool_changed_after_confirmation",
                    True,
                    (start, end),
                )
        # Count-bearing aggregates stay aggregates. No invented individual pass rows.
        for p in parts:
            if re.search(r"station|stn|linear EBUS|nodal", p[2], re.I) or NEGATIVE.search(p[2]):
                continue
            for match in re.finditer(
                r"\b(\d+)\s+(?:passes? (?:of |with )?)?(?:transbronchi\w*\s+)?(needle (?:aspiration|asp)|TBNA|forceps biopsies|(?:\d+(?:\.\d+)?[- ]mm\s+)?(?:transbronchi\w*\s+)?cryobiopsies|brushing)\b",
                p[2],
                re.I,
            ):
                tool_text = match.group(2).lower()
                tool = (
                    "forceps"
                    if "forceps" in tool_text
                    else "cryoprobe"
                    if "cryo" in tool_text
                    else "brush"
                    if "brush" in tool_text
                    else "aspiration_needle"
                )
                span = (p[0] + match.start(), p[0] + match.end())
                put(
                    "sampling_acquisitions",
                    {
                        "sampling_pass_id": stable_id(request.source_digest, f"acq:{span[0]}"),
                        "target_id": target_id,
                        "acquisition_record_granularity": "aggregate_reported",
                        "reported_pass_count": int(match.group(1)),
                        "sampling_tool": tool,
                        "attribution_status": "attributed",
                    },
                    span,
                )
                set_value(f"/targets/{target_index}/sampling_attempted", True, span)
                set_value(f"/targets/{target_index}/diagnostic_attempted", True, span)
                set_value(f"/targets/{target_index}/specimen_obtained", True, span)

    if any(
        p["category"] == "linear_ebus" and p["performance"] in {"performed", "attempted"}
        for p in proposal["procedures"]
    ):
        session_id = stable_id(request.source_digest, "ebus:0")
        put("ebus_sessions", {"ebus_session_id": session_id}, positive[:2])
        station_rows = {}
        node_targets = {}
        for match in re.finditer(
            r"(?:\b(?:stations?|stn|staion)\s*|\b)(" + STATION + r")\b(?:\s+node)?", masked, re.I
        ):
            if masked[max(0, match.start(1) - 1) : match.start(1)] == "." or re.match(
                r"\.\d", masked[match.end(1) :]
            ):
                continue
            # Bare station-like integers must have explicit station/node context.
            context = next((p for p in parts if p[0] <= match.start() < p[1]), None)
            if context is None:
                continue
            context_start, context_end, clause = context
            continuation = bool(
                match.group(1).upper() in {s.upper() for s in station_rows}
                and re.match(r"\s*" + STATION + r"\s+x\s*\d+\b", clause, re.I)
            )
            if not re.search(r"station|stn|staion|\bnode\b", clause, re.I) and not continuation:
                continue
            if re.search(r"\b(?:year|pack|mm|gauge|size)\b", match.group(), re.I):
                continue
            # Avoid matching pass counts and node measurements as station 5/6/7/8/9.
            if re.match(r"\s*(?:mm|passes|needle|cm|G\b)", masked[match.end() :], re.I):
                continue
            station = match.group(1).upper()
            if station.endswith("RS"):
                station = station[:-2] + "Rs"
            if station.endswith("RI"):
                station = station[:-2] + "Ri"
            span = (context_start, context_end)
            if not clause.strip() or len(clause) > 4096:
                continue
            sampled = (
                False
                if re.search(
                    r"not sampled|without sampling|visualized only|inspected only", clause, re.I
                )
                else True
                if re.search(r"sampled|needle passes|passes|TBNA|\bx\s*\d+\b", clause, re.I)
                else None
            )
            survey_id = stable_id(request.source_digest, "station:" + station)
            row = {
                "station_survey_id": survey_id,
                "ebus_session_id": session_id,
                "iaslc_station": station,
                "survey_modality": "EBUS",
                "station_surveyed": True,
                "station_sampled": sampled,
            }
            if re.search(r"visualized|identified|seen", clause, re.I):
                row["station_visualized"] = True
            explicit = re.search(
                r"(?:short[- ]axis\s*(?:of |: )?(\d+(?:\.\d+)?)\s*mm|(\d+(?:\.\d+)?)\s*mm\s*(?:in |on )?(?:the )?short[- ]axis)",
                clause,
                re.I,
            )
            station_tokens = [
                m.group().upper()
                for m in re.finditer(r"(?<![\w.])" + STATION + r"\b(?!\.\d)", clause, re.I)
                if not re.match(r"\s*(?:mm|passes|needle|cm|G\b)", clause[m.end() :], re.I)
            ]
            if explicit and len(set(station_tokens)) == 1:
                row.update(
                    largest_short_axis_mm=float(explicit.group(1) or explicit.group(2)),
                    size_axis_explicit=True,
                )
            elif re.search(r"\d+\s*mm", clause, re.I):
                unresolved.append(
                    {
                        "kind": "node_measurement_axis_unspecified",
                        "station": station,
                        "start": span[0],
                        "end": span[1],
                    }
                )
            if station not in station_rows:
                station_rows[station] = put("station_surveys", row, span)
            else:
                index = station_rows[station]
                previous = proposal["station_surveys"][index]
                for field, value in row.items():
                    path = f"/station_surveys/{index}/{field}"
                    if value is not None and previous.get(field) is None:
                        set_value(path, value, span)
                    elif value is not None and previous.get(field) != value:
                        provenance[path]["conflict_status"] = "unresolved"
                        unresolved.append(
                            {
                                "kind": "station_detail_conflict",
                                "station": station,
                                "field": field,
                                "start": span[0],
                                "end": span[1],
                            }
                        )
                        if field == "station_sampled":
                            previous[field] = None
                            provenance[path]["missingness_reason"] = "unknown"
            if sampled is True:
                # This is a nodal sampling target; individual-node identity remains null.
                target_id = stable_id(request.source_digest, "node-target:" + station)
                target = {
                    "target_id": target_id,
                    "site": "lymph_node",
                    "iaslc_station": station,
                    "station_survey_id": survey_id,
                    "ebus_session_id": session_id,
                    "sampling_attempted": True,
                    "puncture_route": "EBUS",
                }
                count = re.search(r"\b(\d+)\s+(?:needle )?passes\b|\bx\s*(\d+)\b", clause, re.I)
                mentioned = re.findall(
                    r"(?:stations?|stn|staion)\s*(" + STATION + r")\b", clause, re.I
                )
                # Grouped station clauses cannot allocate a shared count to each station.
                if count and len(set(station_tokens)) == 1 and len(mentioned) <= 1:
                    target["needle_pass_count"] = int(count.group(1) or count.group(2))
                if "largest_short_axis_mm" in row:
                    target.update(
                        short_axis_mm=row["largest_short_axis_mm"],
                        size_axis_explicit=True,
                        measurement_modality="EBUS",
                    )
                if station not in node_targets:
                    node_targets[station] = put("targets", target, span)
                else:
                    index = node_targets[station]
                    for field, value in target.items():
                        path = f"/targets/{index}/{field}"
                        previous = proposal["targets"][index].get(field)
                        if previous is None:
                            set_value(path, value, span)
                        elif previous != value:
                            provenance[path]["conflict_status"] = "unresolved"
                            unresolved.append(
                                {
                                    "kind": "station_detail_conflict",
                                    "station": station,
                                    "field": field,
                                    "start": span[0],
                                    "end": span[1],
                                }
                            )
    for p in parts:
        if re.search(
            r"no (?:immediate |other immediate )?complication|without immediate complication|complication[s]?:\s*none|without[^.\n]{0,150}other immediate adverse event",
            p[2],
            re.I,
        ):
            set_value("/complication_assessment", "absent", p[:2])
    complication_sections = []
    for header in re.finditer(r"(?im)^\s*COMPLICATIONS\s*:", masked):
        following = re.search(r"(?m)^\s*[A-Z][A-Z /_-]+:", masked[header.end() :])
        complication_sections.append(
            (header.start(), header.end() + following.start() if following else len(masked))
        )
    for start, end, sentence in parts:
        in_section = any(a <= start < b for a, b in complication_sections)
        if not in_section and not re.search(
            r"\b(?:immediate|intraprocedural|during the procedure)\b", sentence, re.I
        ):
            continue
        for event in re.finditer(
            r"\b(bleeding|pneumothorax|bronchospasm|hypoxemia|hypotension|arrhythmia|respiratory failure)\b",
            sentence,
            re.I,
        ):
            before, after = sentence[: event.start()], sentence[event.end() :]
            if re.search(r"\b(?:no|without|risk of|history of|prior)\b.{0,45}$", before, re.I):
                continue
            if not re.search(
                r"\b(?:treated|controlled|managed|required|requiring|occurred|developed)\b",
                after[:100],
                re.I,
            ):
                continue
            if re.search(r"\b(?:not|never)\b", after[:40], re.I):
                continue
            category = event.group().lower().replace(" ", "_")
            if any(c["category"] == category for c in proposal["complications"]):
                continue
            put(
                "complications",
                {
                    "category": category,
                    "state": "present",
                    "event_time_window": "immediate",
                    "event_treatment_summary": text[start:end].strip(),
                },
                (start, end),
            )
            contradicted = proposal.get("complication_assessment") == "absent"
            set_value("/complication_assessment", "present", (start, end))
            if contradicted:
                provenance["/complication_assessment"]["conflict_status"] = "unresolved"
                unresolved.append(
                    {"kind": "complication_summary_conflict", "start": start, "end": end}
                )
    # Final diagnosis, ROSE, navigation and imaging are deliberately independent.
    proposal["field_provenance"] = list(provenance.values())
    for item in provenance.values():
        if text[item["source_start"] : item["source_end"]] != item["source_excerpt"]:
            raise ValueError("proposal_evidence_mismatch")
    return {
        "proposal": proposal,
        "quality_signals": [{"phase": phase, "status": "completed"} for phase in PHASES],
        "unresolved_mentions": unresolved,
        "ner_spans": list(ner_spans),
    }, sorted(set(warnings))
