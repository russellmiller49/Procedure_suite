from ml.scripts.sanitize_dataset import get_entity_text, repair_bio, sanitize_record


def test_reconstruct_entity_text_subwords() -> None:
    tokens = ["du", "##mon"]
    tags = ["B-PATIENT", "I-PATIENT"]
    entity_text, next_idx = get_entity_text(tokens, tags, 0)

    assert entity_text == "dumon"
    assert next_idx == 2


def test_wipe_ln_station_geo() -> None:
    tokens = ["4", "##r"]
    tags = ["B-GEO", "I-GEO"]

    new_tags = sanitize_record(tokens, tags)

    assert new_tags == ["O", "O"]


def test_wipe_device_mislabeled_patient() -> None:
    tokens = ["du", "##mon"]
    tags = ["B-PATIENT", "I-PATIENT"]

    new_tags = sanitize_record(tokens, tags)

    assert new_tags == ["O", "O"]


def test_wordpiece_reconstruct_catches_mixed_tags_dumon() -> None:
    tokens = ["du", "##mon"]
    tags = ["B-PATIENT", "B-GEO"]

    new_tags = sanitize_record(tokens, tags)

    assert new_tags == ["O", "O"]


def test_cpt_wordpiece_wipe_in_code_context() -> None:
    tokens = ["code", ":", "316", "##53", "("]
    tags = ["O", "O", "B-GEO", "I-GEO", "O"]

    new_tags = sanitize_record(tokens, tags)

    assert new_tags == ["O", "O", "O", "O", "O"]


def test_cpt_wordpiece_wipe_in_codes_context() -> None:
    tokens = ["codes", ":", "316", "##53", "("]
    tags = ["O", "O", "B-GEO", "I-GEO", "O"]

    new_tags = sanitize_record(tokens, tags)

    assert new_tags == ["O", "O", "O", "O", "O"]


def test_cpt_wordpiece_wipe_when_codes_is_split() -> None:
    tokens = ["code", "##s", ":", "316", "##53"]
    tags = ["O", "O", "O", "B-GEO", "I-GEO"]

    new_tags = sanitize_record(tokens, tags)

    assert new_tags == ["O", "O", "O", "O", "O"]


def test_cpt_wordpiece_wipe_in_radiology_guidance_ct_context() -> None:
    tokens = ["radiology", "guidance", "ct", "316", "##53"]
    tags = ["O", "O", "O", "B-GEO", "I-GEO"]

    new_tags = sanitize_record(tokens, tags)

    assert new_tags == ["O", "O", "O", "O", "O"]


def test_cpt_wordpiece_wipe_bullet_radiology_guidance_ct_context() -> None:
    tokens = ["•", "770", "##12", "radiology", "guidance", "ct"]
    tags = ["O", "B-GEO", "I-GEO", "O", "O", "O"]

    new_tags = sanitize_record(tokens, tags)

    assert new_tags == ["O", "O", "O", "O", "O", "O"]


def test_cpt_wordpiece_wipe_with_bullet_token() -> None:
    tokens = ["•", "316", "##53"]
    tags = ["O", "B-GEO", "I-GEO"]

    new_tags = sanitize_record(tokens, tags)

    assert new_tags == ["O", "O", "O"]


def test_cpt_wordpiece_wipe_with_record_level_code_header() -> None:
    tokens = ["la", "jolla", ",", "ca", "920", "##37"]
    tags = ["O", "O", "O", "O", "B-GEO", "I-GEO"]

    new_tags = sanitize_record(tokens, tags, record_text="Codes: 31653")

    assert new_tags == ["O", "O", "O", "O", "O", "O"]


def test_cpt_not_wiped_without_code_context() -> None:
    tokens = ["la", "jolla", ",", "ca", "920", "##37"]
    tags = ["O", "O", "O", "O", "B-GEO", "I-GEO"]

    new_tags = sanitize_record(tokens, tags)

    assert new_tags == tags


def test_ln_station_wordpiece_wipe() -> None:
    tokens = ["4", "##r"]
    tags = ["B-GEO", "I-GEO"]

    new_tags = sanitize_record(tokens, tags)

    assert new_tags == ["O", "O"]


def test_do_not_wipe_real_patient() -> None:
    tokens = ["jennifer", "wu"]
    tags = ["B-PATIENT", "I-PATIENT"]

    new_tags = sanitize_record(tokens, tags)

    assert new_tags == tags


def test_bio_repair_after_wipe() -> None:
    labels = ["O", "I-GEO"]

    repaired = repair_bio(labels)

    assert repaired == ["O", "B-GEO"]
