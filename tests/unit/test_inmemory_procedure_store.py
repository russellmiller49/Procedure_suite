"""Unit tests for InMemoryProcedureStore."""

import pytest

from app.coder.adapters.persistence.inmemory_procedure_store import (
    InMemoryProcedureStore,
    get_default_procedure_store,
    reset_default_procedure_store,
)
from proc_schemas.coding import CodeSuggestion, FinalCode, ReviewAction, CodingResult
from proc_schemas.reasoning import ReasoningFields


@pytest.fixture
def store():
    """Create a fresh InMemoryProcedureStore for each test."""
    return InMemoryProcedureStore()


@pytest.fixture
def sample_suggestion():
    """Create a sample CodeSuggestion."""
    return CodeSuggestion(
        code="31652",
        description="EBUS-TBNA 1-2 stations",
        source="hybrid",
        final_confidence=0.9,
        reasoning=ReasoningFields(kb_version="test_v1", confidence=0.9),
        suggestion_id="sugg_001",
        procedure_id="proc_001",
    )


@pytest.fixture
def sample_final_code():
    """Create a sample FinalCode."""
    return FinalCode(
        code="31652",
        description="EBUS-TBNA 1-2 stations",
        source="hybrid",
        reasoning=ReasoningFields(kb_version="test_v1", confidence=0.9),
        procedure_id="proc_001",
        suggestion_id="sugg_001",
    )


@pytest.fixture
def sample_review():
    """Create a sample ReviewAction."""
    return ReviewAction(
        suggestion_id="sugg_001",
        action="accept",
        reviewer_id="dr_smith",
    )


class TestSuggestionRepository:
    """Tests for suggestion repository methods."""

    def test_save_and_get_suggestions(self, store, sample_suggestion):
        proc_id = "test_001"

        # Initially empty
        assert store.get_suggestions(proc_id) == []
        assert not store.exists(proc_id)

        # Save suggestions
        store.save_suggestions(proc_id, [sample_suggestion])

        # Retrieve
        suggestions = store.get_suggestions(proc_id)
        assert len(suggestions) == 1
        assert suggestions[0].code == "31652"
        assert store.exists(proc_id)

    def test_save_suggestions_overwrites(self, store, sample_suggestion):
        proc_id = "test_002"

        # Save first set
        store.save_suggestions(proc_id, [sample_suggestion])
        assert len(store.get_suggestions(proc_id)) == 1

        # Save second set (overwrites)
        new_suggestion = CodeSuggestion(
            code="31624",
            description="BAL",
            source="rule",
            final_confidence=0.8,
            suggestion_id="sugg_002",
            procedure_id=proc_id,
        )
        store.save_suggestions(proc_id, [new_suggestion])

        suggestions = store.get_suggestions(proc_id)
        assert len(suggestions) == 1
        assert suggestions[0].code == "31624"

    def test_delete_suggestions(self, store, sample_suggestion):
        proc_id = "test_003"

        store.save_suggestions(proc_id, [sample_suggestion])
        assert store.exists(proc_id)

        store.delete_suggestions(proc_id)
        assert not store.exists(proc_id)
        assert store.get_suggestions(proc_id) == []


class TestCodingResultRepository:
    """Tests for coding result repository methods."""

    def test_save_and_get_result(self, store, sample_suggestion):
        proc_id = "test_010"

        # Initially None
        assert store.get_result(proc_id) is None

        # Save result
        result = CodingResult(
            procedure_id=proc_id,
            suggestions=[sample_suggestion],
            kb_version="test_v1",
        )
        store.save_result(proc_id, result)

        # Retrieve
        retrieved = store.get_result(proc_id)
        assert retrieved is not None
        assert retrieved.procedure_id == proc_id
        assert len(retrieved.suggestions) == 1

    def test_delete_result(self, store, sample_suggestion):
        proc_id = "test_011"

        result = CodingResult(
            procedure_id=proc_id,
            suggestions=[sample_suggestion],
        )
        store.save_result(proc_id, result)
        assert store.get_result(proc_id) is not None

        store.delete_result(proc_id)
        assert store.get_result(proc_id) is None


class TestReviewRepository:
    """Tests for review repository methods."""

    def test_add_and_get_reviews(self, store, sample_review):
        proc_id = "test_020"

        # Initially empty
        assert store.get_reviews(proc_id) == []

        # Add review
        store.add_review(proc_id, sample_review)

        reviews = store.get_reviews(proc_id)
        assert len(reviews) == 1
        assert reviews[0].action == "accept"

    def test_add_multiple_reviews(self, store, sample_review):
        proc_id = "test_021"

        store.add_review(proc_id, sample_review)

        second_review = ReviewAction(
            suggestion_id="sugg_002",
            action="reject",
            reviewer_id="dr_jones",
        )
        store.add_review(proc_id, second_review)

        reviews = store.get_reviews(proc_id)
        assert len(reviews) == 2
        assert reviews[0].action == "accept"
        assert reviews[1].action == "reject"

    def test_delete_reviews(self, store, sample_review):
        proc_id = "test_022"

        store.add_review(proc_id, sample_review)
        assert len(store.get_reviews(proc_id)) == 1

        store.delete_reviews(proc_id)
        assert store.get_reviews(proc_id) == []


class TestFinalCodeRepository:
    """Tests for final code repository methods."""

    def test_add_and_get_final_codes(self, store, sample_final_code):
        proc_id = "test_030"

        # Initially empty
        assert store.get_final_codes(proc_id) == []

        # Add final code
        store.add_final_code(proc_id, sample_final_code)

        final_codes = store.get_final_codes(proc_id)
        assert len(final_codes) == 1
        assert final_codes[0].code == "31652"

    def test_add_multiple_final_codes(self, store, sample_final_code):
        proc_id = "test_031"

        store.add_final_code(proc_id, sample_final_code)

        second_code = FinalCode(
            code="31624",
            description="BAL",
            source="rule",
            procedure_id=proc_id,
        )
        store.add_final_code(proc_id, second_code)

        final_codes = store.get_final_codes(proc_id)
        assert len(final_codes) == 2

    def test_delete_final_codes(self, store, sample_final_code):
        proc_id = "test_032"

        store.add_final_code(proc_id, sample_final_code)
        assert len(store.get_final_codes(proc_id)) == 1

        store.delete_final_codes(proc_id)
        assert store.get_final_codes(proc_id) == []


class TestRegistryExportRepository:
    """Tests for registry export repository methods."""

    def test_save_and_get_export(self, store):
        proc_id = "test_040"

        # Initially None
        assert store.get_export(proc_id) is None

        # Save export
        export = {
            "registry_id": "ip_registry",
            "schema_version": "v2",
            "export_id": "exp_001",
            "bundle": {"ebus_performed": True},
        }
        store.save_export(proc_id, export)

        # Retrieve
        retrieved = store.get_export(proc_id)
        assert retrieved is not None
        assert retrieved["export_id"] == "exp_001"
        assert retrieved["bundle"]["ebus_performed"] is True

    def test_export_exists(self, store):
        proc_id = "test_041"

        assert not store.export_exists(proc_id)

        store.save_export(proc_id, {"export_id": "exp_002"})
        assert store.export_exists(proc_id)

    def test_delete_export(self, store):
        proc_id = "test_042"

        store.save_export(proc_id, {"export_id": "exp_003"})
        assert store.get_export(proc_id) is not None

        store.delete_export(proc_id)
        assert store.get_export(proc_id) is None


class TestClearAll:
    """Tests for clear_all method."""

    def test_clear_all_for_procedure(self, store, sample_suggestion, sample_review, sample_final_code):
        proc_id = "test_050"

        # Add data for this procedure
        store.save_suggestions(proc_id, [sample_suggestion])
        store.add_review(proc_id, sample_review)
        store.add_final_code(proc_id, sample_final_code)
        store.save_export(proc_id, {"export_id": "exp_004"})

        # Add data for another procedure
        other_proc = "test_051"
        store.save_suggestions(other_proc, [sample_suggestion])

        # Clear only the first procedure
        store.clear_all(proc_id)

        # First procedure cleared
        assert store.get_suggestions(proc_id) == []
        assert store.get_reviews(proc_id) == []
        assert store.get_final_codes(proc_id) == []
        assert store.get_export(proc_id) is None

        # Other procedure untouched
        assert len(store.get_suggestions(other_proc)) == 1

    def test_clear_all_everything(self, store, sample_suggestion):
        # Add data for multiple procedures
        store.save_suggestions("proc_a", [sample_suggestion])
        store.save_suggestions("proc_b", [sample_suggestion])

        # Clear all
        store.clear_all()

        assert store.get_suggestions("proc_a") == []
        assert store.get_suggestions("proc_b") == []
        assert len(store.get_all_procedure_ids()) == 0


class TestDefaultStore:
    """Tests for the singleton default store."""

    def test_get_default_store(self):
        reset_default_procedure_store()
        store = get_default_procedure_store()
        assert store is not None
        assert isinstance(store, InMemoryProcedureStore)

    def test_default_store_is_singleton(self):
        reset_default_procedure_store()
        store1 = get_default_procedure_store()
        store2 = get_default_procedure_store()
        assert store1 is store2

    def test_reset_clears_data(self):
        store = get_default_procedure_store()
        store.save_export("proc_x", {"export_id": "exp_999"})
        assert store.get_export("proc_x") is not None

        reset_default_procedure_store()
        new_store = get_default_procedure_store()
        assert new_store.get_export("proc_x") is None


class TestStats:
    """Tests for stats helper method."""

    def test_get_stats(self, store, sample_suggestion, sample_review, sample_final_code):
        # Add various data
        store.save_suggestions("proc_1", [sample_suggestion])
        store.save_suggestions("proc_2", [sample_suggestion, sample_suggestion])
        store.add_review("proc_1", sample_review)
        store.add_final_code("proc_1", sample_final_code)

        stats = store.get_stats()
        assert stats["procedures_with_suggestions"] == 2
        assert stats["total_suggestions"] == 3
        assert stats["total_reviews"] == 1
        assert stats["total_final_codes"] == 1
