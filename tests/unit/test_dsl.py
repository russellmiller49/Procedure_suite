"""Unit tests for the JSONLogic-style DSL evaluator.

Tests the modules/common/rules_engine/dsl.py module which provides
a minimal JSONLogic-like DSL for declarative rules evaluation.
"""

import pytest

from app.common.rules_engine.dsl import (
    Rule,
    evaluate_predicate,
    run_rules,
)


class TestEvaluatePredicate:
    """Tests for the evaluate_predicate function."""

    def test_empty_predicate_returns_true(self):
        """Empty predicate {} should evaluate to True."""
        assert evaluate_predicate({}, {}) is True

    def test_literal_values_returned_unchanged(self):
        """Literal values should be returned as-is."""
        assert evaluate_predicate(42, {}) == 42
        assert evaluate_predicate("hello", {}) == "hello"
        assert evaluate_predicate(True, {}) is True
        assert evaluate_predicate(False, {}) is False
        assert evaluate_predicate(None, {}) is None

    def test_list_predicates_evaluated_recursively(self):
        """Lists should have each element evaluated."""
        result = evaluate_predicate([1, {"var": "x"}, 3], {"x": 2})
        assert result == [1, 2, 3]


class TestVarOperator:
    """Tests for the 'var' operator (variable resolution)."""

    def test_var_simple_lookup(self):
        """Simple variable lookup."""
        context = {"name": "test", "count": 5}
        assert evaluate_predicate({"var": "name"}, context) == "test"
        assert evaluate_predicate({"var": "count"}, context) == 5

    def test_var_nested_path(self):
        """Deep variable resolution like 'patient.demographics.age'."""
        context = {
            "patient": {
                "demographics": {
                    "age": 65,
                    "sex": "M",
                }
            }
        }
        assert evaluate_predicate({"var": "patient.demographics.age"}, context) == 65
        assert evaluate_predicate({"var": "patient.demographics.sex"}, context) == "M"

    def test_var_missing_returns_none(self):
        """Missing path should return None, not raise an error."""
        context = {"a": {"b": 1}}
        assert evaluate_predicate({"var": "x"}, context) is None
        assert evaluate_predicate({"var": "a.c"}, context) is None
        assert evaluate_predicate({"var": "a.b.c"}, context) is None

    def test_var_with_non_string_identifier(self):
        """Non-string identifier should be returned as-is."""
        context = {"x": 10}
        assert evaluate_predicate({"var": 42}, context) == 42


class TestLogicalOperators:
    """Tests for logical operators: and, or, not."""

    def test_and_all_true(self):
        """'and' with all truthy values returns True."""
        predicate = {"and": [True, 1, "yes"]}
        assert evaluate_predicate(predicate, {}) is True

    def test_and_one_false(self):
        """'and' with any falsy value returns False."""
        predicate = {"and": [True, 0, "yes"]}
        assert evaluate_predicate(predicate, {}) is False

    def test_and_empty_list(self):
        """'and' with empty list returns True (vacuous truth)."""
        assert evaluate_predicate({"and": []}, {}) is True

    def test_and_short_circuit(self):
        """'and' should short-circuit on first falsy value."""
        # If short-circuiting works, the second element won't be evaluated
        # We test this by using a nested structure that would fail
        predicate = {"and": [False, {"==": ["should_not_evaluate"]}]}
        assert evaluate_predicate(predicate, {}) is False

    def test_or_all_false(self):
        """'or' with all falsy values returns False."""
        predicate = {"or": [False, 0, "", None]}
        assert evaluate_predicate(predicate, {}) is False

    def test_or_one_true(self):
        """'or' with any truthy value returns True."""
        predicate = {"or": [False, 0, 1]}
        assert evaluate_predicate(predicate, {}) is True

    def test_or_empty_list(self):
        """'or' with empty list returns False."""
        assert evaluate_predicate({"or": []}, {}) is False

    def test_or_short_circuit(self):
        """'or' should short-circuit on first truthy value."""
        predicate = {"or": [True, {"==": ["should_not_evaluate"]}]}
        assert evaluate_predicate(predicate, {}) is True

    def test_not_truthy(self):
        """'not' of truthy value returns False."""
        assert evaluate_predicate({"not": True}, {}) is False
        assert evaluate_predicate({"not": 1}, {}) is False
        assert evaluate_predicate({"not": "yes"}, {}) is False

    def test_not_falsy(self):
        """'not' of falsy value returns True."""
        assert evaluate_predicate({"not": False}, {}) is True
        assert evaluate_predicate({"not": 0}, {}) is True
        assert evaluate_predicate({"not": ""}, {}) is True
        assert evaluate_predicate({"not": None}, {}) is True


class TestComparisonOperators:
    """Tests for comparison operators: ==, !=, >, >=, <, <=."""

    def test_equality(self):
        """Test '==' operator."""
        assert evaluate_predicate({"==": [5, 5]}, {}) is True
        assert evaluate_predicate({"==": [5, 6]}, {}) is False
        assert evaluate_predicate({"==": ["a", "a"]}, {}) is True
        assert evaluate_predicate({"==": ["a", "b"]}, {}) is False

    def test_inequality(self):
        """Test '!=' operator."""
        assert evaluate_predicate({"!=": [5, 6]}, {}) is True
        assert evaluate_predicate({"!=": [5, 5]}, {}) is False

    def test_greater_than(self):
        """Test '>' operator."""
        assert evaluate_predicate({">": [10, 5]}, {}) is True
        assert evaluate_predicate({">": [5, 10]}, {}) is False
        assert evaluate_predicate({">": [5, 5]}, {}) is False

    def test_greater_or_equal(self):
        """Test '>=' operator."""
        assert evaluate_predicate({">=": [10, 5]}, {}) is True
        assert evaluate_predicate({">=": [5, 5]}, {}) is True
        assert evaluate_predicate({">=": [5, 10]}, {}) is False

    def test_less_than(self):
        """Test '<' operator."""
        assert evaluate_predicate({"<": [5, 10]}, {}) is True
        assert evaluate_predicate({"<": [10, 5]}, {}) is False
        assert evaluate_predicate({"<": [5, 5]}, {}) is False

    def test_less_or_equal(self):
        """Test '<=' operator."""
        assert evaluate_predicate({"<=": [5, 10]}, {}) is True
        assert evaluate_predicate({"<=": [5, 5]}, {}) is True
        assert evaluate_predicate({"<=": [10, 5]}, {}) is False

    def test_comparison_with_var(self):
        """Comparisons should resolve variables."""
        context = {"age": 30, "threshold": 25}
        assert evaluate_predicate({">": [{"var": "age"}, {"var": "threshold"}]}, context) is True
        assert evaluate_predicate({"<=": [{"var": "age"}, 25]}, context) is False

    def test_type_mismatch_comparison(self):
        """Test comparing different types (string vs int)."""
        # Python allows this but behavior may vary
        # The DSL should pass through to Python's comparison
        # Note: In Python 3, comparing str and int raises TypeError
        with pytest.raises(TypeError):
            evaluate_predicate({">": ["10", 5]}, {})


class TestInOperator:
    """Tests for the 'in' membership operator."""

    def test_in_list(self):
        """Test membership in a list."""
        assert evaluate_predicate({"in": [3, [1, 2, 3, 4]]}, {}) is True
        assert evaluate_predicate({"in": [5, [1, 2, 3, 4]]}, {}) is False

    def test_in_string(self):
        """Test substring membership."""
        assert evaluate_predicate({"in": ["bc", "abcd"]}, {}) is True
        assert evaluate_predicate({"in": ["xy", "abcd"]}, {}) is False

    def test_in_with_var(self):
        """Test 'in' with variable resolution."""
        context = {"code": "31652", "allowed_codes": ["31652", "31653", "31654"]}
        predicate = {"in": [{"var": "code"}, {"var": "allowed_codes"}]}
        assert evaluate_predicate(predicate, context) is True


class TestIfOperator:
    """Tests for the 'if' ternary operator."""

    def test_if_true_branch(self):
        """Test 'if' selects true branch when condition is truthy."""
        predicate = {"if": [True, "yes", "no"]}
        assert evaluate_predicate(predicate, {}) == "yes"

    def test_if_false_branch(self):
        """Test 'if' selects false branch when condition is falsy."""
        predicate = {"if": [False, "yes", "no"]}
        assert evaluate_predicate(predicate, {}) == "no"

    def test_if_with_var_condition(self):
        """Test 'if' with variable-based condition."""
        context = {"is_adult": True}
        predicate = {"if": [{"var": "is_adult"}, "adult", "minor"]}
        assert evaluate_predicate(predicate, context) == "adult"

        context["is_adult"] = False
        assert evaluate_predicate(predicate, context) == "minor"


class TestErrorHandling:
    """Tests for error handling in the DSL."""

    def test_multiple_operators_raises(self):
        """Predicate with multiple operators should raise ValueError."""
        predicate = {">": [10, 5], "<": [10, 20]}
        with pytest.raises(ValueError, match="single operator"):
            evaluate_predicate(predicate, {})

    def test_unsupported_operator_raises(self):
        """Unknown operator should raise KeyError."""
        predicate = {"unknown_op": [1, 2]}
        with pytest.raises(KeyError, match="Unsupported operator"):
            evaluate_predicate(predicate, {})


class TestRunRules:
    """Tests for the run_rules function."""

    def test_run_rules_returns_matching_actions(self):
        """run_rules should return actions for matching rules."""
        rules = [
            Rule(name="rule1", when=True, action={"cpt": "31652"}),
            Rule(name="rule2", when=False, action={"cpt": "31653"}),
            Rule(name="rule3", when={"var": "is_active"}, action={"cpt": "31654"}),
        ]
        context = {"is_active": True}

        results = run_rules(rules, context)

        assert len(results) == 2
        assert {"cpt": "31652"} in results
        assert {"cpt": "31654"} in results
        assert {"cpt": "31653"} not in results

    def test_run_rules_empty_list(self):
        """run_rules with empty rules list returns empty list."""
        assert run_rules([], {}) == []

    def test_run_rules_no_matches(self):
        """run_rules with no matching rules returns empty list."""
        rules = [
            Rule(name="rule1", when=False, action={"cpt": "31652"}),
            Rule(name="rule2", when={">": [5, 10]}, action={"cpt": "31653"}),
        ]
        assert run_rules(rules, {}) == []

    def test_run_rules_with_complex_predicates(self):
        """run_rules with complex nested predicates."""
        rules = [
            Rule(
                name="ebus_3plus",
                when={
                    "and": [
                        {"var": "ebus_performed"},
                        {">=": [{"var": "stations_count"}, 3]},
                    ]
                },
                action={"cpt": "31653", "confidence": 1.0},
            ),
            Rule(
                name="ebus_1_2",
                when={
                    "and": [
                        {"var": "ebus_performed"},
                        {"<": [{"var": "stations_count"}, 3]},
                    ]
                },
                action={"cpt": "31652", "confidence": 1.0},
            ),
        ]

        context = {"ebus_performed": True, "stations_count": 4}
        results = run_rules(rules, context)
        assert len(results) == 1
        assert results[0]["cpt"] == "31653"

        context = {"ebus_performed": True, "stations_count": 2}
        results = run_rules(rules, context)
        assert len(results) == 1
        assert results[0]["cpt"] == "31652"

        context = {"ebus_performed": False, "stations_count": 5}
        results = run_rules(rules, context)
        assert len(results) == 0


class TestRuleDataclass:
    """Tests for the Rule dataclass."""

    def test_rule_creation(self):
        """Test creating a Rule instance."""
        rule = Rule(
            name="test_rule",
            when={"var": "x"},
            action={"do": "something"},
        )
        assert rule.name == "test_rule"
        assert rule.when == {"var": "x"}
        assert rule.action == {"do": "something"}

    def test_rule_slots(self):
        """Rule should use slots for memory efficiency."""
        rule = Rule(name="test", when=True, action={})
        assert hasattr(rule, "__slots__")


class TestComplexScenarios:
    """Integration tests with complex real-world-like scenarios."""

    def test_bronchoscopy_coding_rules(self):
        """Test rules similar to bronchoscopy CPT coding decisions."""
        rules = [
            Rule(
                name="tblb_performed",
                when={"var": "tblb.performed"},
                action={"cpt": "31628", "description": "TBLB"},
            ),
            Rule(
                name="bal_performed",
                when={"var": "bal.performed"},
                action={"cpt": "31624", "description": "BAL"},
            ),
            Rule(
                name="navigation_with_tblb",
                when={
                    "and": [
                        {"var": "navigation.performed"},
                        {"var": "tblb.performed"},
                    ]
                },
                action={"cpt": "31627", "description": "Navigation"},
            ),
        ]

        context = {
            "tblb": {"performed": True},
            "bal": {"performed": True},
            "navigation": {"performed": True},
        }

        results = run_rules(rules, context)
        cpts = [r["cpt"] for r in results]

        assert "31628" in cpts  # TBLB
        assert "31624" in cpts  # BAL
        assert "31627" in cpts  # Navigation

    def test_threshold_based_decision(self):
        """Test rules with numeric thresholds."""
        rules = [
            Rule(
                name="high_confidence",
                when={">=": [{"var": "ml_confidence"}, 0.9]},
                action={"decision": "auto_accept"},
            ),
            Rule(
                name="gray_zone",
                when={
                    "and": [
                        {">=": [{"var": "ml_confidence"}, 0.5]},
                        {"<": [{"var": "ml_confidence"}, 0.9]},
                    ]
                },
                action={"decision": "llm_review"},
            ),
            Rule(
                name="low_confidence",
                when={"<": [{"var": "ml_confidence"}, 0.5]},
                action={"decision": "manual_review"},
            ),
        ]

        # High confidence case
        results = run_rules(rules, {"ml_confidence": 0.95})
        assert len(results) == 1
        assert results[0]["decision"] == "auto_accept"

        # Gray zone case
        results = run_rules(rules, {"ml_confidence": 0.7})
        assert len(results) == 1
        assert results[0]["decision"] == "llm_review"

        # Low confidence case
        results = run_rules(rules, {"ml_confidence": 0.3})
        assert len(results) == 1
        assert results[0]["decision"] == "manual_review"
