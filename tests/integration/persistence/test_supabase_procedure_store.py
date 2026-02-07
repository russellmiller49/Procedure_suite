"""Supabase ProcedureStore smoke tests.

These tests verify that SupabaseProcedureStore can connect and perform
basic CRUD operations. They are SKIPPED by default unless explicitly enabled.

To run these tests:
    1. Set up Supabase credentials:
       export SUPABASE_URL="https://your-project.supabase.co"
       export SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"

    2. Enable the tests:
       export RUN_SUPABASE_TESTS=1

    3. Run pytest:
       pytest tests/integration/persistence/test_supabase_procedure_store.py -v

Note: These tests use a unique test prefix to avoid conflicts with production data.
All test data is cleaned up after each test.
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime

import pytest

# Check if Supabase tests should run
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
RUN_SUPABASE_TESTS = os.getenv("RUN_SUPABASE_TESTS", "").lower() in ("1", "true", "yes")

# Skip conditions
supabase_not_configured = not (SUPABASE_URL and SUPABASE_KEY)
supabase_tests_disabled = not RUN_SUPABASE_TESTS

skip_reason = (
    "Supabase tests disabled (set RUN_SUPABASE_TESTS=1 to enable)"
    if supabase_tests_disabled
    else "Supabase credentials not configured (set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY)"
    if supabase_not_configured
    else None
)

pytestmark = pytest.mark.skipif(
    supabase_tests_disabled or supabase_not_configured,
    reason=skip_reason or "Unknown",
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture(scope="module")
def supabase_store():
    """Create a SupabaseProcedureStore for testing.

    This fixture is module-scoped to avoid repeatedly connecting to Supabase.
    """
    from app.coder.adapters.persistence.supabase_procedure_store import (
        SupabaseProcedureStore,
    )

    store = SupabaseProcedureStore()
    yield store


@pytest.fixture
def test_proc_id():
    """Generate a unique procedure ID for testing.

    Uses a prefix to make test data identifiable.
    """
    return f"test-supabase-{uuid.uuid4().hex[:8]}"


@pytest.fixture(autouse=True)
def cleanup_test_data(supabase_store, test_proc_id):
    """Clean up test data after each test."""
    yield
    # Clean up after test
    try:
        supabase_store.clear_all(test_proc_id)
    except Exception:
        pass  # Best effort cleanup


# ============================================================================
# Connection Tests
# ============================================================================


class TestSupabaseConnection:
    """Tests for Supabase connectivity."""

    def test_is_supabase_available(self):
        """Test that is_supabase_available returns True when configured."""
        from app.coder.adapters.persistence.supabase_procedure_store import (
            is_supabase_available,
        )

        assert is_supabase_available() is True

    def test_can_create_store(self, supabase_store):
        """Test that SupabaseProcedureStore can be instantiated."""
        assert supabase_store is not None

    def test_get_stats_works(self, supabase_store):
        """Test that get_stats() can query all tables without error."""
        stats = supabase_store.get_stats()
        assert isinstance(stats, dict)
        # Should have keys for various counts
        assert "total_suggestions" in stats or stats == {}


# ============================================================================
# Suggestion CRUD Tests
# ============================================================================


class TestSuggestionsCRUD:
    """Tests for CodeSuggestion save/get roundtrip."""

    def test_save_and_get_suggestions_roundtrip(self, supabase_store, test_proc_id):
        """Test that suggestions can be saved and retrieved."""
        from proc_schemas.coding import CodeSuggestion

        # Create test suggestions
        suggestions = [
            CodeSuggestion(
                code="31652",
                description="EBUS-TBNA 1-2 stations",
                source="rule",
                final_confidence=0.9,
                suggestion_id=f"sug-{uuid.uuid4().hex[:8]}",
                procedure_id=test_proc_id,
            ),
            CodeSuggestion(
                code="31624",
                description="BAL",
                source="hybrid",
                final_confidence=0.85,
                suggestion_id=f"sug-{uuid.uuid4().hex[:8]}",
                procedure_id=test_proc_id,
            ),
        ]

        # Save suggestions
        supabase_store.save_suggestions(test_proc_id, suggestions)

        # Retrieve suggestions
        retrieved = supabase_store.get_suggestions(test_proc_id)

        # Verify
        assert len(retrieved) == 2
        codes = {s.code for s in retrieved}
        assert codes == {"31652", "31624"}

    def test_exists_returns_true_after_save(self, supabase_store, test_proc_id):
        """Test that exists() returns True after saving suggestions."""
        from proc_schemas.coding import CodeSuggestion

        # Initially should not exist
        assert supabase_store.exists(test_proc_id) is False

        # Save a suggestion
        suggestions = [
            CodeSuggestion(
                code="31652",
                description="Test",
                source="rule",
                final_confidence=0.9,
                suggestion_id=f"sug-{uuid.uuid4().hex[:8]}",
                procedure_id=test_proc_id,
            )
        ]
        supabase_store.save_suggestions(test_proc_id, suggestions)

        # Now should exist
        assert supabase_store.exists(test_proc_id) is True

    def test_delete_suggestions(self, supabase_store, test_proc_id):
        """Test that suggestions can be deleted."""
        from proc_schemas.coding import CodeSuggestion

        # Save a suggestion
        suggestions = [
            CodeSuggestion(
                code="31652",
                description="Test",
                source="rule",
                final_confidence=0.9,
                suggestion_id=f"sug-{uuid.uuid4().hex[:8]}",
                procedure_id=test_proc_id,
            )
        ]
        supabase_store.save_suggestions(test_proc_id, suggestions)
        assert supabase_store.exists(test_proc_id) is True

        # Delete
        supabase_store.delete_suggestions(test_proc_id)
        assert supabase_store.exists(test_proc_id) is False


# ============================================================================
# CodingResult CRUD Tests
# ============================================================================


class TestCodingResultCRUD:
    """Tests for CodingResult save/get roundtrip."""

    def test_save_and_get_result_roundtrip(self, supabase_store, test_proc_id):
        """Test that coding results can be saved and retrieved."""
        from proc_schemas.coding import CodingResult

        # Create test result
        result = CodingResult(
            procedure_id=test_proc_id,
            procedure_type="bronch_ebus",
            kb_version="test-1.0",
            policy_version="test-1.0",
            model_version="test-1.0",
            processing_time_ms=150.5,
            llm_latency_ms=75.2,
        )

        # Save result
        supabase_store.save_result(test_proc_id, result)

        # Retrieve result
        retrieved = supabase_store.get_result(test_proc_id)

        # Verify
        assert retrieved is not None
        assert retrieved.procedure_id == test_proc_id
        assert retrieved.procedure_type == "bronch_ebus"
        assert retrieved.processing_time_ms == 150.5
        assert retrieved.llm_latency_ms == 75.2

    def test_get_result_returns_none_for_missing(self, supabase_store, test_proc_id):
        """Test that get_result returns None for non-existent procedure."""
        result = supabase_store.get_result(test_proc_id)
        assert result is None


# ============================================================================
# FinalCode CRUD Tests
# ============================================================================


class TestFinalCodesCRUD:
    """Tests for FinalCode save/get roundtrip."""

    def test_add_and_get_final_codes(self, supabase_store, test_proc_id):
        """Test that final codes can be added and retrieved."""
        from proc_schemas.coding import FinalCode

        # Add final codes
        code1 = FinalCode(
            code="31652",
            description="EBUS-TBNA 1-2 stations",
            source="hybrid",
            procedure_id=test_proc_id,
            work_rvu=3.5,
        )
        code2 = FinalCode(
            code="31624",
            description="BAL",
            source="rule",
            procedure_id=test_proc_id,
            work_rvu=1.2,
        )

        supabase_store.add_final_code(test_proc_id, code1)
        supabase_store.add_final_code(test_proc_id, code2)

        # Retrieve
        retrieved = supabase_store.get_final_codes(test_proc_id)

        # Verify
        assert len(retrieved) == 2
        codes = {fc.code for fc in retrieved}
        assert codes == {"31652", "31624"}


# ============================================================================
# Review CRUD Tests
# ============================================================================


class TestReviewsCRUD:
    """Tests for ReviewAction save/get roundtrip."""

    def test_add_and_get_reviews(self, supabase_store, test_proc_id):
        """Test that reviews can be added and retrieved."""
        from proc_schemas.coding import ReviewAction

        # Add reviews
        review1 = ReviewAction(
            suggestion_id="sug-001",
            action="accept",
            reviewer_id="dr-test",
        )
        review2 = ReviewAction(
            suggestion_id="sug-002",
            action="reject",
            reviewer_id="dr-test",
            notes="Not supported by documentation",
        )

        supabase_store.add_review(test_proc_id, review1)
        supabase_store.add_review(test_proc_id, review2)

        # Retrieve
        retrieved = supabase_store.get_reviews(test_proc_id)

        # Verify
        assert len(retrieved) == 2
        actions = {r.action for r in retrieved}
        assert actions == {"accept", "reject"}


# ============================================================================
# Registry Export CRUD Tests
# ============================================================================


class TestRegistryExportsCRUD:
    """Tests for registry export save/get roundtrip."""

    def test_save_and_get_export(self, supabase_store, test_proc_id):
        """Test that exports can be saved and retrieved."""
        # Create export record
        export = {
            "registry_id": "ip_registry",
            "schema_version": "v2",
            "export_id": f"exp-{uuid.uuid4().hex[:8]}",
            "export_timestamp": datetime.utcnow().isoformat(),
            "status": "success",
            "bundle": {
                "procedure_id": test_proc_id,
                "ebus_performed": True,
                "bal_performed": True,
            },
            "warnings": [],
        }

        # Save export
        supabase_store.save_export(test_proc_id, export)

        # Retrieve
        retrieved = supabase_store.get_export(test_proc_id)

        # Verify
        assert retrieved is not None
        assert retrieved["export_id"] == export["export_id"]
        assert retrieved["bundle"]["ebus_performed"] is True

    def test_export_exists(self, supabase_store, test_proc_id):
        """Test that export_exists works correctly."""
        # Should not exist initially
        assert supabase_store.export_exists(test_proc_id) is False

        # Save export
        export = {
            "registry_id": "ip_registry",
            "schema_version": "v2",
            "export_id": f"exp-{uuid.uuid4().hex[:8]}",
            "status": "success",
            "bundle": {},
        }
        supabase_store.save_export(test_proc_id, export)

        # Should exist now
        assert supabase_store.export_exists(test_proc_id) is True


# ============================================================================
# Clear All Tests
# ============================================================================


class TestClearAll:
    """Tests for clear_all functionality."""

    def test_clear_all_for_procedure(self, supabase_store, test_proc_id):
        """Test that clear_all removes all data for a procedure."""
        from proc_schemas.coding import CodeSuggestion, FinalCode, ReviewAction

        # Add data of all types
        supabase_store.save_suggestions(
            test_proc_id,
            [
                CodeSuggestion(
                    code="31652",
                    source="rule",
                    final_confidence=0.9,
                    suggestion_id="sug-001",
                    procedure_id=test_proc_id,
                )
            ],
        )
        supabase_store.add_final_code(
            test_proc_id,
            FinalCode(code="31652", source="hybrid", procedure_id=test_proc_id),
        )
        supabase_store.add_review(
            test_proc_id,
            ReviewAction(suggestion_id="sug-001", action="accept", reviewer_id="test"),
        )
        supabase_store.save_export(
            test_proc_id,
            {"export_id": "exp-001", "status": "success", "bundle": {}},
        )

        # Verify data exists
        assert supabase_store.exists(test_proc_id) is True
        assert len(supabase_store.get_final_codes(test_proc_id)) > 0

        # Clear all
        supabase_store.clear_all(test_proc_id)

        # Verify all gone
        assert supabase_store.exists(test_proc_id) is False
        assert len(supabase_store.get_final_codes(test_proc_id)) == 0
        assert len(supabase_store.get_reviews(test_proc_id)) == 0
        assert supabase_store.get_export(test_proc_id) is None
