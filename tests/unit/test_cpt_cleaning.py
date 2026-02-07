from ml.lib.ml_coder.utils import clean_cpt_codes


def test_clean_cpt_codes_basic():
    assert clean_cpt_codes("316,273,165,431,628") == ["31627", "31654", "31628"]


def test_clean_cpt_codes_short_values():
    assert clean_cpt_codes("3,260,932,650") == ["32609", "32650"]


def test_clean_cpt_codes_handles_null():
    assert clean_cpt_codes(None) == []
