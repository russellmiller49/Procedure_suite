#!/usr/bin/env python3
"""
Terminology Normalization Utilities for IP Coding Knowledge Base

This module provides functions to normalize terminology using the
terminology_mappings section of the IP coding JSON.

Usage:
    from terminology_utils import TerminologyNormalizer
    
    normalizer = TerminologyNormalizer('data/knowledge/ip_coding_billing_v2_9.json')
    
    # Normalize user input to canonical key
    canonical = normalizer.to_canonical('conscious sedation')  # → 'moderate_sedation'
    
    # Get display label for UI
    display = normalizer.to_display('moderate_sedation')  # → 'Moderate Sedation'
    
    # Full normalization with category: input → canonical → display
    result = normalizer.normalize_with_category('mod sed')
    # → {'canonical_key': 'moderate_sedation', 'display_label': 'Moderate Sedation', 'category': 'procedure_categories'}
    
    # Tokenized matching: find matches within longer text
    matches = normalizer.find_terms_in_text('Patient underwent EBUS-TBNA of station 7 subcarinal node')
    # → [{'term': 'ebus-tbna', 'canonical_key': 'ebus', ...}, {'term': 'subcarinal', 'canonical_key': '7', ...}]

Author: IP Coding Assistant
Version: 1.1
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional


# Default JSON path - update this when releasing new versions
DEFAULT_JSON_PATH = Path("data/knowledge/ip_coding_billing_v2_9.json")
KNOWLEDGE_ENV_VAR = "PSUITE_KNOWLEDGE_FILE"


def _load_knowledge_source(source: str | Path | Dict[str, Any] | None) -> Dict[str, Any]:
    if isinstance(source, dict):
        return source
    path = Path(source) if source else Path(os.getenv(KNOWLEDGE_ENV_VAR, DEFAULT_JSON_PATH))
    if not path.exists():
        raise FileNotFoundError(f"Knowledge file not found: {path}")
    with open(path, "r") as handle:
        return json.load(handle)


class TerminologyNormalizer:
    """Normalize terminology using the IP coding knowledge base mappings."""
    
    def __init__(self, knowledge_source: str | Path | Dict[str, Any] | None = None):
        """
        Initialize normalizer with a path or pre-loaded knowledge dictionary.
        
        Args:
            knowledge_source: Path to the knowledge JSON or a parsed dictionary.
        """
        data = _load_knowledge_source(knowledge_source)
        self.mappings = data.get('terminology_mappings', {})
        
        # Build reverse lookup: variation → (category, canonical_key, display_label)
        self._variation_index = {}
        # Also build a list of all variations sorted by length (longest first) for tokenized matching
        self._variations_by_length = []
        
        for category, items in self.mappings.items():
            if category.startswith('_') or not isinstance(items, dict):
                continue
            for key, entry in items.items():
                if not isinstance(entry, dict):
                    continue
                canonical = entry.get('canonical_key', key)
                display = entry.get('display_label', canonical)
                for variation in entry.get('variations', []):
                    normalized_var = self._normalize_string(variation)
                    entry_data = {
                        'category': category,
                        'canonical_key': canonical,
                        'display_label': display,
                        'original_variation': variation
                    }
                    self._variation_index[normalized_var] = entry_data
                    self._variations_by_length.append((normalized_var, entry_data))
        
        # Sort by length descending for greedy matching
        self._variations_by_length.sort(key=lambda x: len(x[0]), reverse=True)
    
    def _normalize_string(self, s: str) -> str:
        """Normalize string for lookup: lowercase, strip, collapse whitespace."""
        return re.sub(r'\s+', ' ', s.lower().strip())
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words and multi-word phrases for matching.
        Returns all possible n-grams up to 5 words.
        """
        # Normalize and split
        normalized = self._normalize_string(text)
        words = normalized.split()
        
        tokens = []
        # Generate n-grams from 1 to 5 words
        for n in range(1, min(6, len(words) + 1)):
            for i in range(len(words) - n + 1):
                tokens.append(' '.join(words[i:i+n]))
        
        return tokens
    
    def to_canonical(self, term: str, category: Optional[str] = None) -> Optional[str]:
        """
        Convert a term to its canonical key.
        
        Args:
            term: Input term (e.g., 'conscious sedation', 'mod sed')
            category: Optional category to restrict search (e.g., 'procedure_categories')
            
        Returns:
            Canonical key (e.g., 'moderate_sedation') or None if not found
        """
        normalized = self._normalize_string(term)
        result = self._variation_index.get(normalized)
        
        if result:
            if category is None or result['category'] == category:
                return result['canonical_key']
        
        return None
    
    def to_display(self, canonical_key: str, category: Optional[str] = None) -> Optional[str]:
        """
        Convert a canonical key to its display label.
        
        Args:
            canonical_key: Canonical key (e.g., 'moderate_sedation')
            category: Optional category to search in
            
        Returns:
            Display label (e.g., 'Moderate Sedation') or None if not found
        """
        categories_to_search = [category] if category else self.mappings.keys()
        
        for cat in categories_to_search:
            if cat.startswith('_'):
                continue
            items = self.mappings.get(cat, {})
            if not isinstance(items, dict):
                continue
            for key, entry in items.items():
                if not isinstance(entry, dict):
                    continue
                if entry.get('canonical_key') == canonical_key:
                    return entry.get('display_label')
        
        return None
    
    def normalize(self, term: str, category: Optional[str] = None) -> Optional[Dict[str, str]]:
        """
        Full normalization: term → canonical_key → display_label.
        
        Args:
            term: Input term
            category: Optional category to restrict search
            
        Returns:
            Dict with 'canonical_key' and 'display_label', or None
        """
        normalized = self._normalize_string(term)
        result = self._variation_index.get(normalized)
        
        if result:
            if category is None or result['category'] == category:
                return {
                    'canonical_key': result['canonical_key'],
                    'display_label': result['display_label']
                }
        
        return None
    
    def normalize_with_category(self, term: str, category: Optional[str] = None) -> Optional[Dict[str, str]]:
        """
        Full normalization with category included: term → canonical_key → display_label + category.
        
        This is useful when you need to distinguish between terms from different
        categories (e.g., a procedure name vs. a device name).
        
        Args:
            term: Input term
            category: Optional category to restrict search
            
        Returns:
            Dict with 'canonical_key', 'display_label', and 'category', or None
        """
        normalized = self._normalize_string(term)
        result = self._variation_index.get(normalized)
        
        if result:
            if category is None or result['category'] == category:
                return {
                    'canonical_key': result['canonical_key'],
                    'display_label': result['display_label'],
                    'category': result['category']
                }
        
        return None
    
    def find_terms_in_text(self, text: str, categories: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Find all known terminology within a longer text using tokenized matching.
        
        This method tokenizes the input text and searches for any known variations
        within it. It uses greedy matching (longest matches first) to avoid
        duplicate/overlapping matches.
        
        Args:
            text: Input text to search (e.g., procedure note, clinical text)
            categories: Optional list of categories to restrict search
            
        Returns:
            List of match dictionaries, each containing:
            - 'term': The matched term as it appeared in text
            - 'canonical_key': The canonical key
            - 'display_label': The display label
            - 'category': The category
            - 'start': Start position in normalized text
            - 'end': End position in normalized text
        """
        normalized_text = self._normalize_string(text)
        matches = []
        matched_ranges = []  # Track already-matched character ranges
        
        # Try to match each variation, longest first
        for variation, entry_data in self._variations_by_length:
            if categories and entry_data['category'] not in categories:
                continue
            
            # Find all occurrences of this variation
            start = 0
            while True:
                pos = normalized_text.find(variation, start)
                if pos == -1:
                    break
                
                end = pos + len(variation)
                
                # Check if this range overlaps with any already-matched range
                overlaps = False
                for (m_start, m_end) in matched_ranges:
                    if not (end <= m_start or pos >= m_end):
                        overlaps = True
                        break
                
                if not overlaps:
                    # Check word boundaries (don't match partial words)
                    before_ok = (pos == 0 or not normalized_text[pos-1].isalnum())
                    after_ok = (end == len(normalized_text) or not normalized_text[end].isalnum())
                    
                    if before_ok and after_ok:
                        matches.append({
                            'term': variation,
                            'canonical_key': entry_data['canonical_key'],
                            'display_label': entry_data['display_label'],
                            'category': entry_data['category'],
                            'start': pos,
                            'end': end
                        })
                        matched_ranges.append((pos, end))
                
                start = pos + 1
        
        # Sort matches by position
        matches.sort(key=lambda x: x['start'])
        
        return matches
    
    def extract_terms(self, text: str, categories: Optional[List[str]] = None) -> Dict[str, List[str]]:
        """
        Extract and group terms from text by category.
        
        Convenience wrapper around find_terms_in_text that groups results
        by category and returns only the canonical keys.
        
        Args:
            text: Input text to search
            categories: Optional list of categories to restrict search
            
        Returns:
            Dict mapping category → list of canonical keys found
        """
        matches = self.find_terms_in_text(text, categories)
        
        result = {}
        for match in matches:
            cat = match['category']
            if cat not in result:
                result[cat] = []
            if match['canonical_key'] not in result[cat]:
                result[cat].append(match['canonical_key'])
        
        return result
    
    def get_all_variations(self, canonical_key: str) -> List[str]:
        """Get all recognized variations for a canonical key."""
        variations = []
        for norm_var, data in self._variation_index.items():
            if data['canonical_key'] == canonical_key:
                variations.append(norm_var)
        return variations
    
    def list_categories(self) -> List[str]:
        """List all available terminology categories."""
        return [k for k in self.mappings.keys() if not k.startswith('_')]
    
    def list_terms(self, category: str) -> List[str]:
        """List all canonical terms in a category."""
        items = self.mappings.get(category, {})
        if not isinstance(items, dict):
            return []
        return [
            entry.get('canonical_key') 
            for entry in items.values() 
            if isinstance(entry, dict)
        ]


class CodeListHelper:
    """Helper for working with flattened code_lists."""
    
    def __init__(self, knowledge_source: str | Path | Dict[str, Any] | None = None):
        data = _load_knowledge_source(knowledge_source)
        self.code_lists = data.get('code_lists', {})
    
    def get_codes(self, key: str) -> List[str]:
        """Get codes for a given key."""
        return self.code_lists.get(key, [])
    
    def get_codes_by_prefix(self, prefix: str) -> Dict[str, List[str]]:
        """Get all code lists matching a prefix."""
        return {k: v for k, v in self.code_lists.items() if k.startswith(prefix)}
    
    def find_code(self, cpt_code: str) -> List[str]:
        """Find which code lists contain a given CPT code."""
        normalized = cpt_code.lstrip('+')
        with_plus = f'+{normalized}'
        found_in = []
        for key, codes in self.code_lists.items():
            if normalized in codes or with_plus in codes or cpt_code in codes:
                found_in.append(key)
        return found_in
    
    def list_all_keys(self) -> List[str]:
        """List all code list keys."""
        return list(self.code_lists.keys())


class QARuleChecker:
    """Check QA/documentation rules for CPT add-on codes."""
    
    def __init__(self, knowledge_source: str | Path | Dict[str, Any] | None = None):
        data = _load_knowledge_source(knowledge_source)
        raw_rules = data.get('qa_rules', {}) or {}
        self.qa_rules: Dict[str, Dict[str, Any]] = {
            name: rule for name, rule in raw_rules.items() if not name.startswith('_')
        }
        self._code_index = self._build_code_index()
    
    def _build_code_index(self) -> Dict[str, List[str]]:
        index: Dict[str, List[str]] = {}
        for name, rule in self.qa_rules.items():
            code_lists = []
            for key in ("codes", "radial_codes"):
                values = rule.get(key) or []
                if isinstance(values, str):
                    values = [values]
                code_lists.extend(values)
            for code in code_lists:
                normalized = str(code).lstrip("+")
                index.setdefault(normalized, []).append(name)
        return index
    
    def get_rule(self, rule_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific QA rule by name."""
        return self.qa_rules.get(rule_name)
    
    def list_rules(self) -> List[str]:
        """List all QA rule names."""
        return list(self.qa_rules.keys())
    
    def evaluate_code(self, code: str, documentation: Mapping[str, Any]) -> List[Dict[str, Any]]:
        """
        Evaluate all rules associated with a CPT code.
        
        Returns a list of failing rule evaluations (empty list if all pass).
        """
        normalized = code.lstrip("+")
        failures = []
        for rule_name in self._code_index.get(normalized, []):
            rule = self.qa_rules.get(rule_name)
            if not rule:
                continue
            result = self._evaluate_rule(rule, documentation)
            if not result["passed"]:
                result["rule"] = rule_name
                result["description"] = rule.get("description", "")
                failures.append(result)
        return failures
    
    def check_navigation(self, documentation: Mapping[str, Any]) -> Dict[str, Any]:
        """Convenience wrapper for the navigation QA rule."""
        return self._evaluate_named_rule('navigation_required', documentation)
    
    def check_radial_ebus(self, documentation: Mapping[str, Any]) -> Dict[str, Any]:
        """Convenience wrapper for the radial EBUS QA rule."""
        return self._evaluate_named_rule('radial_requires_peripheral_sampling', documentation)
    
    def _evaluate_named_rule(self, name: str, documentation: Mapping[str, Any]) -> Dict[str, Any]:
        rule = self.qa_rules.get(name, {})
        result = self._evaluate_rule(rule, documentation)
        result["rule"] = name
        result["description"] = rule.get("description", "")
        return result
    
    def _evaluate_rule(self, rule: Dict[str, Any], documentation: Mapping[str, Any]) -> Dict[str, Any]:
        required = rule.get('documentation_required', []) or []
        missing = []
        for req in required:
            key = self._normalize_label(req)
            if not self._doc_has_value(documentation, key):
                missing.append(req)
        return {
            'passed': len(missing) == 0,
            'missing': missing,
            'action': rule.get('action', 'flag_for_review'),
        }
    
    @staticmethod
    def _normalize_label(label: str) -> str:
        slug = re.sub(r'[^a-z0-9]+', '_', label.lower()).strip('_')
        return slug
    
    def _doc_has_value(self, documentation: Mapping[str, Any], key: str) -> bool:
        candidates = [key]
        if key.endswith("_used"):
            candidates.append(key[:-4])
        if key.endswith("_documented"):
            candidates.append(key[:-11])
        for candidate in candidates:
            value = documentation.get(candidate)
            if isinstance(value, str):
                if value.strip():
                    return True
            elif isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
                if any(bool(item) for item in value):
                    return True
            elif value:
                return True
        return False


def demo():
    """Demonstrate usage of the utility classes."""
    import sys
    default_path = os.getenv(KNOWLEDGE_ENV_VAR, str(DEFAULT_JSON_PATH))
    json_path = sys.argv[1] if len(sys.argv) > 1 else default_path
    
    print("=" * 70)
    print("TERMINOLOGY NORMALIZER DEMO")
    print("=" * 70)
    
    normalizer = TerminologyNormalizer(json_path)
    
    test_terms = ["conscious sedation", "mod sed", "EBUS-TBNA", "pleurx catheter",
                  "Right Upper Lobe", "subcarinal", "modifier 59", "ZZZ"]
    
    print("\n1. Basic normalization (normalize_with_category):")
    for term in test_terms:
        result = normalizer.normalize_with_category(term)
        if result:
            print(f"   '{term}' → {result['canonical_key']} → '{result['display_label']}' [{result['category']}]")
        else:
            print(f"   '{term}' → NOT FOUND")
    
    print("\n" + "-" * 70)
    print("2. Tokenized text matching (find_terms_in_text):")
    
    sample_texts = [
        "Patient underwent EBUS-TBNA of station 7 subcarinal node",
        "Placed pleurx catheter in right pleural space under moderate sedation",
        "Navigation bronchoscopy with TBLB of RUL lesion"
    ]
    
    for text in sample_texts:
        print(f"\n   Input: \"{text}\"")
        matches = normalizer.find_terms_in_text(text)
        if matches:
            for m in matches:
                print(f"     → '{m['term']}' = {m['canonical_key']} [{m['category']}]")
        else:
            print("     → No matches found")
    
    print("\n" + "-" * 70)
    print("3. Extract and group terms by category:")
    
    text = "Performed diagnostic bronchoscopy with BAL and TBLB of right lower lobe under moderate sedation"
    print(f"\n   Input: \"{text}\"")
    grouped = normalizer.extract_terms(text)
    for category, terms in grouped.items():
        print(f"     {category}: {terms}")
    
    print("\n" + "=" * 70)
    print("CODE LIST HELPER DEMO")
    print("=" * 70)
    
    helper = CodeListHelper(json_path)
    print("\nBLVR-related code lists:")
    for key, codes in helper.get_codes_by_prefix('bronchoscopic_blvr').items():
        print(f"  {key}: {codes}")
    print(f"\nFinding code 31647: {helper.find_code('31647')}")
    
    print("\n" + "=" * 70)
    print("QA RULE CHECKER DEMO")
    print("=" * 70)
    
    checker = QARuleChecker(json_path)
    print(f"\nAvailable QA rules: {checker.list_rules()}")
    
    result = checker.check_navigation({'navigation_system': True, 'catheter_advanced': True, 'target_identified': True})
    print(f"\nNavigation (complete): passed={result['passed']}")
    
    result = checker.check_navigation({'navigation_system': True, 'catheter_advanced': False, 'target_identified': True})
    print(f"Navigation (incomplete): passed={result['passed']}, missing={result['missing']}")


if __name__ == "__main__":
    demo()
