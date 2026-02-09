from __future__ import annotations

from app.reporting.util.path_access import get_path
from app.reporting.validation import _expand_list_paths


def test_get_path_missing_dict_key_returns_none() -> None:
    data = {"a": {"b": 1}}
    assert get_path(data, "a.c") is None
    assert get_path(data, "a.b.c") is None


def test_get_path_list_index_out_of_range_returns_none() -> None:
    data = {"a": [{"b": 1}]}
    assert get_path(data, "a[1].b") is None
    assert get_path(data, "a[-2].b") is None


def test_get_path_list_vs_dict_drift_returns_none() -> None:
    assert get_path({"a": [{"b": 1}]}, "a.b") is None
    assert get_path({"a": {"b": 1}}, "a[0].b") is None


def test_expand_list_paths_missing_or_empty_list() -> None:
    assert _expand_list_paths({}, "stations[].passes") == ["stations[0].passes"]
    assert _expand_list_paths({"stations": []}, "stations[].passes") == ["stations[0].passes"]


def test_expand_list_paths_expands_existing_list() -> None:
    payload = {"stations": [{"passes": 1}, {"passes": 2}]}
    assert _expand_list_paths(payload, "stations[].passes") == ["stations[0].passes", "stations[1].passes"]


def test_expand_list_paths_supports_nested_placeholders() -> None:
    payload = {
        "outer": [
            {"inner": [{"x": 1}, {"x": 2}]},
            {"inner": [{"x": 3}]},
        ]
    }
    assert _expand_list_paths(payload, "outer[].inner[].x") == [
        "outer[0].inner[0].x",
        "outer[0].inner[1].x",
        "outer[1].inner[0].x",
    ]

