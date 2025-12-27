from __future__ import annotations

from scripts.distill_phi_labels import (
    extract_procedure_codes,
    is_protected_for_person,
    is_protected_for_geo,
    looks_like_real_address,
    normalize_entity_group,
    refine_teacher_spans,
    repair_bio,
    wipe_cpt_subword_labels,
    wipe_ln_station_labels,
)


def test_refine_drops_cpt_zipcode_when_in_cpt_list() -> None:
    text = "CPT: 31654"
    start = text.index("31654")
    end = start + len("31654")
    spans = [{"start": start, "end": end, "entity_group": "ZIPCODE", "score": 0.9}]

    refined = refine_teacher_spans(
        text,
        spans,
        cpt_codes_set={"31654"},
        enable_refinery=True,
        drop_zipcode_if_cpt=True,
        drop_buildingnum_if_temp=True,
        provider_policy="drop",
        provider_label="PROVIDER",
        label_schema="standard",
    )

    assert refined == []


def test_refine_keeps_zipcode_in_address() -> None:
    text = "La Jolla, CA 92037"
    start = text.index("92037")
    end = start + len("92037")
    spans = [{"start": start, "end": end, "entity_group": "ZIPCODE", "score": 0.9}]

    refined = refine_teacher_spans(
        text,
        spans,
        cpt_codes_set=set(),
        enable_refinery=True,
        drop_zipcode_if_cpt=True,
        drop_buildingnum_if_temp=True,
        provider_policy="drop",
        provider_label="PROVIDER",
        label_schema="standard",
    )

    assert len(refined) == 1


def test_refine_drops_temperature_buildingnum() -> None:
    text = "RFA deployed. 105C for 10 min"
    start = text.index("105C")
    end = start + len("105C")
    spans = [{"start": start, "end": end, "entity_group": "BUILDINGNUM", "score": 0.9}]

    refined = refine_teacher_spans(
        text,
        spans,
        cpt_codes_set=set(),
        enable_refinery=True,
        drop_zipcode_if_cpt=True,
        drop_buildingnum_if_temp=True,
        provider_policy="drop",
        provider_label="PROVIDER",
        label_schema="standard",
    )

    assert refined == []


def test_refine_keeps_buildingnum_in_address() -> None:
    text = "9300 Campus Point Dr"
    spans = [{"start": 0, "end": 4, "entity_group": "BUILDINGNUM", "score": 0.9}]

    refined = refine_teacher_spans(
        text,
        spans,
        cpt_codes_set=set(),
        enable_refinery=True,
        drop_zipcode_if_cpt=True,
        drop_buildingnum_if_temp=True,
        provider_policy="drop",
        provider_label="PROVIDER",
        label_schema="standard",
    )

    assert len(refined) == 1


def test_label_schema_mapping() -> None:
    assert normalize_entity_group("GIVENNAME", "standard", "PROVIDER") == "PATIENT"
    assert normalize_entity_group("ZIPCODE", "standard", "PROVIDER") == "GEO"
    assert normalize_entity_group("PROVIDER", "standard", "PROVIDER") == "PROVIDER"


def test_subword_cpt_wipe_for_geo_labels() -> None:
    tokens = ["CPT", ":", "316", "##54"]
    labels = ["O", "O", "B-GEO", "I-GEO"]
    cleaned = wipe_cpt_subword_labels(tokens, labels, cpt_codes_set={"31654"})
    assert cleaned == ["O", "O", "O", "O"]


def test_subword_zipcode_not_wiped_without_cpt_signal() -> None:
    tokens = ["La", "Jolla", ",", "CA", "920", "##37"]
    labels = ["O", "O", "O", "O", "B-GEO", "I-GEO"]
    cleaned = wipe_cpt_subword_labels(tokens, labels, cpt_codes_set=set())
    assert cleaned == labels


def test_subword_cpt_wipe_for_zipcode_labels() -> None:
    tokens = ["316", "##54"]
    labels = ["B-ZIPCODE", "I-ZIPCODE"]
    cleaned = wipe_cpt_subword_labels(tokens, labels, cpt_codes_set={"31654"})
    assert cleaned == ["O", "O"]


def test_protected_anatomy_veto() -> None:
    assert is_protected_for_geo("Left Upper Lobe")


def test_protected_device_veto() -> None:
    assert is_protected_for_person("Dumon")


def test_station_veto() -> None:
    assert is_protected_for_geo("4R")
    assert is_protected_for_geo("10R")
    assert is_protected_for_geo("7")
    assert is_protected_for_person("11Rs")


def test_address_plausibility_true() -> None:
    line = "9300 Campus Point Dr, La Jolla, CA 92037"
    assert looks_like_real_address("9300 Campus Point Dr", line)


def test_address_plausibility_false() -> None:
    line = "Station 4R sampled"
    assert not looks_like_real_address("4R", line)


def test_span_gate_drops_geo_without_evidence() -> None:
    text = "Left Upper Lobe mass"
    start = text.index("Left")
    end = start + len("Left Upper Lobe")
    spans = [{"start": start, "end": end, "entity_group": "STREETNAME", "score": 0.9}]
    refined = refine_teacher_spans(
        text,
        spans,
        cpt_codes_set=set(),
        enable_refinery=True,
        drop_zipcode_if_cpt=True,
        drop_buildingnum_if_temp=True,
        provider_policy="drop",
        provider_label="PROVIDER",
        label_schema="standard",
    )
    assert refined == []


def test_extract_procedure_codes_from_text_section() -> None:
    record = {"cpt_codes": []}
    text = "Codes Submitted:\\n31654\\n31655\\n\\nOther section"
    codes = extract_procedure_codes(record, text)
    assert {"31654", "31655"}.issubset(codes)


def test_repair_bio_fix_i_tag() -> None:
    tags = ["O", "I-GEO", "I-GEO"]
    assert repair_bio(tags) == ["O", "B-GEO", "I-GEO"]


def test_ln_station_split_token_wipe() -> None:
    tokens = ["4", "##r", ",", "7", ",", "10", "##r"]
    labels = ["B-GEO", "I-GEO", "O", "B-GEO", "O", "B-GEO", "I-GEO"]
    cleaned = wipe_ln_station_labels(tokens, labels)
    assert cleaned == ["O", "O", "O", "O", "O", "O", "O"]


def test_ln_station_two_letter_wipe() -> None:
    tokens = ["11", "##r", "##s"]
    labels = ["B-GEO", "I-GEO", "I-GEO"]
    cleaned = wipe_ln_station_labels(tokens, labels)
    assert cleaned == ["O", "O", "O"]


def test_dumon_span_dropped_from_person_label() -> None:
    text = "Dumon stent placed"
    spans = [{"start": 0, "end": 5, "entity_group": "GIVENNAME", "score": 0.9}]
    refined = refine_teacher_spans(
        text,
        spans,
        cpt_codes_set=set(),
        enable_refinery=True,
        drop_zipcode_if_cpt=True,
        drop_buildingnum_if_temp=True,
        provider_policy="drop",
        provider_label="PROVIDER",
        label_schema="standard",
    )
    assert refined == []
