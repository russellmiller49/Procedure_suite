import json
from pathlib import Path

from app.umls.ip_umls_store import DistilledUmlsStore


def _load_fixture_store() -> DistilledUmlsStore:
    path = Path(__file__).resolve().parents[1] / "fixtures" / "ip_umls_map.small.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    return DistilledUmlsStore(payload)


def test_distilled_umls_store_match_exact() -> None:
    store = _load_fixture_store()
    match = store.match("Right  upper   lobe", category="anatomy")
    assert match is not None
    assert match["match_type"] == "exact"
    assert match["chosen_cui"] == "C0001"
    assert match["preferred_name"] == "Right upper lobe"


def test_distilled_umls_store_match_loose() -> None:
    store = _load_fixture_store()
    match = store.match("EBUS TBNA")
    assert match is not None
    assert match["match_type"] == "loose"
    assert match["chosen_cui"] == "C0002"


def test_distilled_umls_store_match_category_prefers_matching_concept() -> None:
    store = _load_fixture_store()
    match = store.match("rb1", category="anatomy")
    assert match is not None
    assert match["chosen_cui"] == "C0003"
    assert "anatomy" in match["categories"]


def test_distilled_umls_store_suggest_prefix() -> None:
    store = _load_fixture_store()
    results = store.suggest("rb", category="anatomy", limit=10)
    assert results
    assert all(r["term"].startswith("rb") for r in results)
    assert all("anatomy" in (r.get("categories") or []) for r in results)

