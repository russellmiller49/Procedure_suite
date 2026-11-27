"""Bind report details to explicit operative target/site blocks.

This reporter-only reconciliation runs while seeding, never while editing a
bundle. It does not change registry flags, coding, or the shared schema. A
complete, recognizable narrative block outranks document-wide scalar guesses.
Unrecognized note formats retain the existing adapter path.
"""

from __future__ import annotations

import re

from proc_schemas.clinical import ProcedureBundle, ProcedureInput

_NAV_START = re.compile(r"(?im)^[ \t]*Robotic navigation bronchoscopy was performed with [^\n.]+\.")
_END = re.compile(
    r"(?im)^[ \t]*(?:EBUS[- ]Findings|SPECIMEN\(S\)|IMPRESSION/PLAN|"
    r"ESTIMATED BLOOD LOSS|COMPLICATIONS)\s*:?"
)
_SITE = re.compile(r"(?im)^[ \t]*Site\s+\d+\s*:\s*The\s+(11R[is]|[124]R|[124]L|7|10[RL]|11[RL])\b")
_SAMPLING = re.compile(
    r"(?im)^[ \t]*(Transbronchial needle aspiration|Transbronchial cryobiopsy|"
    r"Transbronchial biopsy|Transbronchial brushing|Bronchial alveolar lavage) was performed\b"
)
_TARGET_TYPES = {
    "robotic_navigation",
    "radial_ebus_survey",
    "radial_ebus_sampling",
    "transbronchial_needle_aspiration",
    "transbronchial_cryobiopsy",
    "transbronchial_biopsy",
    "transbronchial_lung_biopsy",
    "bronchial_brushings",
    "bal",
    "fiducial_marker_placement",
    "cbct_cact_fusion",
    "tool_in_lesion_confirmation",
}
_CBCT_PARAGRAPH = re.compile(r"(?im)^[^\n]*\bCone Beam CT was performed\b[^\n]*")
_ATTESTATION = r"I personally performed and interpreted the CT guidance images"
_TOOL_IN_LESION = r"(?i)\btool[- ]in[- ]lesion\b"


def is_operative_block_note(text: str | None) -> bool:
    """True for the operative-report layout this module reconciles."""
    text = text or ""
    return bool(_NAV_START.search(text) or re.search(r"(?im)^[ \t]*EBUS[- ]Findings\b", text))


def _sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", _clean(text) + ".") if part.strip()]
_FIDUCIAL = re.compile(r"(?im)^[ \t]*Fiducial marker\b[ \t]*(?:\(([^)\n]+)\))?([^\n]*)")


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().rstrip(".")


def _match(pattern: str, text: str) -> str | None:
    match = re.search(pattern, text, re.I)
    if not match:
        return None
    return _clean(next(group for group in match.groups() if group is not None))


def _proc(kind: str, index: str, data: dict) -> ProcedureInput:
    return ProcedureInput(
        proc_type=kind,
        schema_id=f"{kind}_v1",
        proc_id=f"{kind}_source_{index}",
        data=data,
    )


def _section(text: str, heading: str) -> str | None:
    match = re.search(r"(?im)^[ \t]*" + re.escape(heading) + r"[ \t]*:[ \t]*", text)
    if not match:
        return None
    body = text[match.end() :]
    end = re.search(r"(?m)^[ \t]*[A-Z][A-Z ()/]+[ \t]*:", body)
    return body[: end.start() if end else len(body)].strip() or None


def _target_procedures(text: str) -> list[ProcedureInput] | None:
    starts = list(_NAV_START.finditer(text))
    if not starts:
        return None
    procedures: list[ProcedureInput] = []
    for index, start in enumerate(starts, 1):
        block = text[start.start() : starts[index].start() if index < len(starts) else len(text)]
        end = _END.search(block)
        if end:
            block = block[: end.start()]
        location = _match(r"catheter was used to engage the\s+([^\n.]+)", block)
        if not location:
            # Do not partially replace a multi-target report.
            return None
        platform = _match(r"performed with\s+([^\n.]+?)\s+platform", block)
        registration = _match(r"\b(Partial|Full|Automatic) registration was used", block)
        size = _match(r"Target lesion is about\s+(\d+(?:\.\d+)?\s*(?:cm|mm))\b", block)
        distance = _match(r"advanced to\s+(\d+(?:\.\d+)?\s*cm)\s+away", block)
        rose = _match(r"ROSE from ION procedure was noted to be:[ \t]*\n?[ \t]*([^\n]+)", block)
        notes = []
        if size:
            notes.append(f"Target lesion is about {size} in diameter.")
        if distance:
            notes.append(
                "Under navigational guidance the robotic catheter was advanced to "
                f"{distance} away from the planned target."
            )
        if rose:
            notes.append(f"ROSE from the target was noted to be: {rose}.")
        procedures.append(
            _proc(
                "robotic_navigation",
                str(index),
                {
                    "platform": platform,
                    "lesion_location": location,
                    "registration_method": registration,
                    "notes": " ".join(notes) or None,
                },
            )
        )
        pattern = _match(
            r"Radial EBUS was performed[^\n]*?(?:nodule is\s+([^\n.]+)|which showed\s+(\w+)\s+pattern)",
            block,
        )
        if pattern:
            procedures.append(
                _proc(
                    "radial_ebus_survey",
                    str(index),
                    {
                        "location": location,
                        "rebus_features": pattern,
                        "notes": _match(r"following features (?:were )?noted:\s*([^\n]+)", block),
                    },
                )
            )
        # Each documented spin keeps its own source wording. The attestation is
        # carried as a flag and tool-in-lesion as its own step, so neither is
        # repeated inside the notes.
        confirmed = False
        for spin_index, spin in enumerate(_CBCT_PARAGRAPH.finditer(block), 1):
            before, _, after = spin[0].partition("Cone Beam CT was performed")
            kept = []
            for sentence in _sentences(before) + _sentences(after.lstrip(": ")):
                if re.search(_ATTESTATION, sentence, re.I):
                    continue
                if re.search(_TOOL_IN_LESION, sentence):
                    confirmed = True
                    continue
                kept.append(sentence)
            procedures.append(
                ProcedureInput(
                    proc_type="cbct_cact_fusion",
                    schema_id="cbct_cact_fusion_v1",
                    proc_id=f"cbct_cact_fusion_{spin_index}_source_{index}",
                    data={
                        "notes": " ".join(kept) or None,
                        "physician_interpreted": True
                        if re.search(_ATTESTATION, spin[0], re.I)
                        else None,
                    },
                )
            )
        if confirmed:
            procedures.append(
                _proc(
                    "tool_in_lesion_confirmation",
                    str(index),
                    {"confirmation_method": "cone-beam CT"},
                )
            )
        samples = list(_SAMPLING.finditer(block))
        for sample_index, sample in enumerate(samples):
            detail = block[
                sample.start() : samples[sample_index + 1].start()
                if sample_index + 1 < len(samples)
                else len(block)
            ]
            # Each step is a paragraph. Do not borrow a count/result from a later step.
            detail = re.split(r"\n[ \t]*\n", detail, maxsplit=1)[0]
            count = _match(r"Total\s+(\d{1,3})\s+sample(?:s|\(s\))?\s+were collected", detail)
            tests = _match(r"Samples sent for\s+([^\n.]+)", detail)
            data = {"lung_segment": location, "tests": [tests] if tests else []}
            name = sample.group(1).lower()
            if name == "transbronchial cryobiopsy":
                probe = _match(r"(\d+(?:\.\d+)?)\s*mm cryoprobe", detail)
                freeze = _match(r"Freeze time of\s+([\d]+(?:\s*[-–]\s*\d+)?)\s+seconds", detail)
                data.update(
                    num_samples=int(count) if count else None,
                    cryoprobe_size_mm=float(probe) if probe else None,
                    freeze_seconds=int(freeze) if freeze and freeze.isdigit() else None,
                    notes=f"Freeze time: {freeze} seconds"
                    if freeze and not freeze.isdigit()
                    else None,
                )
                kind = "transbronchial_cryobiopsy"
            elif name == "bronchial alveolar lavage":
                volumes = re.search(
                    r"Instilled\s+(\d+)\s*cc[^.]*?returned with\s+(\d+)\s*cc", detail, re.I
                )
                data.update(
                    instilled_volume_cc=int(volumes[1]) if volumes else None,
                    returned_volume_cc=int(volumes[2]) if volumes else None,
                )
                pooled = re.search(
                    r"instillation of\s+(\d+)\s*cc[^.]*?return of\s+(\d+)\s*cc[^.]*?pooled",
                    detail,
                    re.I,
                )
                if pooled and volumes:
                    data["instilled_volume_cc"] += int(pooled[1])
                    data["returned_volume_cc"] += int(pooled[2])
                kind = "bal"
            else:
                data["samples_collected"] = int(count) if count else None
                if name == "transbronchial needle aspiration":
                    gauges = re.findall(r"\b(\d{2})\s*G\s+Needle", detail, re.I)
                    data["needle_gauge"] = ", ".join(f"{g}G" for g in dict.fromkeys(gauges)) or None
                    kind = "transbronchial_needle_aspiration"
                elif name == "transbronchial brushing":
                    data["brush_tool"] = _match(
                        r"performed with\s+(.+?)\s+(?:through\s+)?the extended", detail
                    )
                    kind = "bronchial_brushings"
                else:
                    data["forceps_tools"] = _match(
                        r"performed with\s+(.+?)\s+(?:through\s+)?the extended", detail
                    )
                    kind = "transbronchial_lung_biopsy"
            procedures.append(_proc(kind, str(index), data))
        # The marker belongs to the target block that documents it, not to a
        # lobe guessed from elsewhere in the note.
        marker = _FIDUCIAL.search(block)
        if marker and not re.search(r"(?i)\bnot (?:placed|deployed)\b", marker[0]):
            procedures.append(
                _proc(
                    "fiducial_marker_placement",
                    str(index),
                    {
                        "airway_location": location,
                        "marker_details": _clean(marker[1]) if marker[1] else None,
                        "confirmation_method": "fluoroscopy"
                        if re.search(r"(?i)fluoroscop", marker[2] or "")
                        else None,
                    },
                )
            )
    return procedures


def reconcile_operative_blocks(bundle: ProcedureBundle, text: str) -> ProcedureBundle:
    """Preserve target-local facts and distinguish sampled from inspected nodes."""
    target_procs = _target_procedures(text)
    ebus_start = re.search(r"(?im)^[ \t]*EBUS[- ]Findings\b", text)
    if target_procs is None and ebus_start is None:
        return bundle
    bundle = bundle.model_copy(deep=True)
    if target_procs is not None:
        bundle.procedures = [
            p for p in bundle.procedures if p.proc_type not in _TARGET_TYPES
        ] + target_procs
        ventilation = re.search(
            r"Mode\s+RR\s+TV\s+PEEP\s+FiO2\s+Flow Rate\s+Pmean\s*\n"
            r"[ \t]*(\w+)\s+(\d+)\s+(\d+)\s+(\d+(?:\.\d+)?)\s+"
            r"(\d+)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)",
            text,
            re.I,
        )
        if ventilation:
            fields = dict(
                zip(
                    (
                        "vent_mode",
                        "vent_rr",
                        "vent_tv_ml",
                        "vent_peep_cm_h2o",
                        "vent_fio2_pct",
                        "vent_flow_rate",
                        "vent_pmean_cm_h2o",
                    ),
                    (
                        ventilation[1],
                        int(ventilation[2]),
                        int(ventilation[3]),
                        float(ventilation[4]),
                        int(ventilation[5]),
                        ventilation[6],
                        float(ventilation[7]),
                    ),
                    strict=True,
                )
            )
            first_nav = next(
                (p for p in bundle.procedures if p.proc_type == "robotic_navigation"), None
            )
            if first_nav is not None:
                # The legacy Ion block is not rendered beside robotic_navigation,
                # so the documented settings travel with the first target.
                sentence = (
                    f"Ventilation parameters: Mode {ventilation[1]}, RR {ventilation[2]}, "
                    f"TV {ventilation[3]}, PEEP {ventilation[4]}, FiO2 {ventilation[5]}, "
                    f"Flow Rate {ventilation[6]}, Pmean {ventilation[7]}."
                )
                first_nav.data = {
                    **first_nav.data,
                    "notes": " ".join(filter(None, [first_nav.data.get("notes"), sentence])),
                }
            for proc in bundle.procedures:
                if proc.proc_type == "robotic_ion_bronchoscopy":
                    payload = (
                        proc.data.model_dump()
                        if hasattr(proc.data, "model_dump")
                        else dict(proc.data)
                    )
                    proc.data = {**payload, **fields}
    # Keep explicit diagnoses and the submitted specimen inventory instead of
    # summaries synthesized earlier from document-wide counts.
    for heading, field in (
        ("PREOPERATIVE DIAGNOSIS", "preop_diagnosis_text"),
        ("POSTOPERATIVE DIAGNOSIS", "postop_diagnosis_text"),
        ("SPECIMEN(S)", "specimens_text"),
        ("ESTIMATED BLOOD LOSS", "estimated_blood_loss"),
        ("IMPRESSION/PLAN", "impression_plan"),
    ):
        value = _section(text, heading)
        if value:
            if heading == "POSTOPERATIVE DIAGNOSIS" and value.rstrip(".").lower() == "same":
                value = bundle.preop_diagnosis_text or value
            setattr(bundle, field, value)

    if ebus_start:
        # A lavage of another lobe documented after the nodal work is its own step.
        bundle.procedures = [
            p for p in bundle.procedures if not (p.proc_id or "").startswith("bal_post_ebus_")
        ]
        for number, lavage in enumerate(
            re.finditer(
                r"(?im)^[ \t]*Bronchial alveolar lavage was performed at\s+([^\n.]+)\.([^\n]*)",
                text[ebus_start.end() :],
            ),
            1,
        ):
            volumes = re.search(
                r"Instilled\s+(\d+)\s*cc[^.]*?returned with\s+(\d+)\s*cc", lavage[2], re.I
            )
            tests = _match(r"Samples sent for\s+([^\n.]+)", lavage[2])
            bundle.procedures.append(
                ProcedureInput(
                    proc_type="bal",
                    schema_id="bal_v1",
                    proc_id=f"bal_post_ebus_{number}",
                    data={
                        "lung_segment": _clean(lavage[1]),
                        "instilled_volume_cc": int(volumes[1]) if volumes else None,
                        "returned_volume_cc": int(volumes[2]) if volumes else None,
                        "tests": [tests] if tests else [],
                    },
                )
            )

    closing = re.search(r"(?im)^[ \t]*(The patient tolerated the procedure well\.[^\n]*)", text)
    if closing:
        bundle.closing_text = _clean(closing[1]) + "."

    if ebus_start:
        ebus = text[ebus_start.end() :]
        end = _END.search(ebus)
        if end:
            ebus = ebus[: end.start()]
        sites = list(_SITE.finditer(ebus))
        stations, survey = [], []
        elastography_used = bool(
            re.search(r"\belastography was performed\b|\belastographic pattern\b", ebus, re.I)
        )
        technique = _match(
            r"(All lymph node stations were assessed\.[ \t]*Only those[^\n.]+)\.", ebus
        )
        technique = technique + "." if technique else None
        inspected_block = re.search(
            r"(?is)Lymph Nodes/Sites Inspected:\s*(.+?)(?:\n[ \t]*\n|\Z)", ebus
        )
        inspected = (
            list(
                dict.fromkeys(
                    m.upper()
                    for m in re.findall(
                        r"(?im)^[ \t]*(11R[is]|[124]R|[124]L|7|10[RL]|11[RL])\b",
                        inspected_block[1],
                    )
                )
            )
            if inspected_block
            else []
        )

        def shared_pattern(items: list[dict]) -> str | None:
            patterns = {item.get("elastography_pattern") for item in items}
            return patterns.pop() if len(patterns) == 1 else None

        for index, site in enumerate(sites):
            detail = ebus[
                site.start() : sites[index + 1].start() if index + 1 < len(sites) else len(ebus)
            ]
            station = site[1].upper()
            sampled = bool(re.search(r"\bThe site was sampled\b", detail, re.I))
            not_sampled = bool(re.search(r"\bThe site was not sampled\b", detail, re.I))
            if not sampled and not not_sampled:
                # Only reconcile when every site states its sampling status.
                break
            elastography = _match(r"\b(Type\s+[123])\s+elastographic pattern", detail)
            if not_sampled:
                survey.append(
                    {
                        "station_name": station,
                        "sampled": False,
                        "elastography_pattern": elastography,
                        "comments": _match(r"node was\s+(.+?\bon CT)\b", detail),
                    }
                )
                continue
            count = _match(
                r"\b(\d{1,3})\s+endobronchial ultrasound guided transbronchial biopsies", detail
            )
            rose = _match(r"Preliminary ROSE Cytology was reported as\s+([^\n.]+)", detail)
            stations.append(
                {
                    "station_name": station,
                    "passes": int(count) if count else None,
                    "elastography_pattern": elastography,
                    "biopsy_tools": ["TBNA"],
                    "rose_result": rose,
                    # CT size thresholds are not exact EBUS measurements.
                    "comments": _match(r"node was\s+(.+?\bon CT)\b", detail),
                }
            )
        else:
            if sites:
                bundle.procedures = [p for p in bundle.procedures if p.proc_type != "ebus_tbna"]
                if stations:
                    overall = _match(r"Overall EBUS TBNA ROSE Diagnosis:[ \t]*([^\n]+)", ebus)
                    gauges = re.findall(r"\b(\d{2})-gauge Needle", ebus, re.I)
                    bundle.procedures.append(
                        _proc(
                            "ebus_tbna",
                            "nodes",
                            {
                                "stations": stations,
                                "needle_gauge": ", ".join(f"{g}G" for g in dict.fromkeys(gauges))
                                or None,
                                "elastography_used": True if elastography_used else None,
                                "elastography_pattern": shared_pattern(stations),
                                "survey_technique": technique,
                                "stations_inspected": inspected,
                                "rose_available": False
                                if overall and re.fullmatch(r"not performed", overall, re.I)
                                else None,
                                "overall_rose_diagnosis": overall,
                            },
                        )
                    )
                if survey:
                    bundle.procedures = [
                        p for p in bundle.procedures if p.proc_type != "ebus_survey"
                    ]
                    bundle.procedures.append(
                        _proc(
                            "ebus_survey",
                            "nodes",
                            {
                                "stations": survey,
                                "elastography_used": True if elastography_used else None,
                                "elastography_pattern": shared_pattern(survey),
                                # The technique sentence is already carried by the
                                # sampling block when both are present.
                                "survey_technique": None if stations else technique,
                            },
                        )
                    )
    return bundle
