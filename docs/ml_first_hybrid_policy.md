# ML-First Hybrid Policy

## Overview

The hybrid coding system uses a tiered approach where:

1. **ML = Primary Coder** - Machine learning model generates initial code predictions
2. **RulesEngine = Hard Veto** - Declarative rules validate and filter ML output
3. **LLM = Fallback** - Large language model handles gray zones, low confidence, or rule conflicts

## Configuration

Settings are defined in `data/rules/coding_rules.v1.json` under the `hybrid_policy` key:

```json
{
  "hybrid_policy": {
    "ml_first": true,
    "rules_veto_enabled": true,
    "llm_fallback_enabled": true,
    "rare_code_llm_only_threshold": 10,
    "allowed_auto_ml_codes": ["31622", "31627", "31628", "31654", "32554", "32555", "32550"]
  }
}
```

### Policy Settings

| Setting | Type | Description |
|---------|------|-------------|
| `ml_first` | bool | ML model generates initial predictions |
| `rules_veto_enabled` | bool | Rules engine can veto ML predictions |
| `llm_fallback_enabled` | bool | LLM handles ambiguous cases |
| `rare_code_llm_only_threshold` | int | Codes with fewer than N training examples bypass ML |
| `allowed_auto_ml_codes` | array | Codes safe for fully automated ML prediction |

## Per-Code Guardrails

Individual codes can have guardrail metadata in `code_metadata`:

```json
{
  "31641": {
    "allow_auto_ml": true,
    "requires_navigation_for_addons": ["31627", "31654"]
  },
  "31634": {
    "allow_auto_ml": false,
    "llm_only": true
  },
  "31629": {
    "allow_auto_ml": false,
    "requires_removal_evidence": true
  }
}
```

### Guardrail Fields

| Field | Type | Description |
|-------|------|-------------|
| `allow_auto_ml` | bool | Whether ML can auto-assign this code |
| `llm_only` | bool | Code must be evaluated by LLM only |
| `requires_navigation_for_addons` | array | Add-on codes that require navigation context |
| `requires_removal_evidence` | bool | Code requires explicit removal evidence |

## Decision Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     Input Document                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              ML Model (Primary Coder)                       │
│  • Generates initial code predictions                       │
│  • Provides confidence scores                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│             Rules Engine (Hard Veto)                        │
│  • Validates codes against evidence requirements            │
│  • Removes codes that fail 4-gate checks                    │
│  • Applies mutual exclusion rules                           │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────────┐
│   High Confidence       │     │   Low Confidence / Conflict │
│   → Final Output        │     │   → LLM Fallback            │
└─────────────────────────┘     └─────────────────────────────┘
                                              │
                                              ▼
                                ┌─────────────────────────────┐
                                │   LLM Evaluation            │
                                │   • Gray zone resolution    │
                                │   • Rule conflict handling  │
                                │   • Rare code assessment    │
                                └─────────────────────────────┘
```

## When LLM Fallback Triggers

- ML confidence below threshold
- Rules engine produces conflicting decisions
- Code is marked `llm_only: true`
- Code has fewer examples than `rare_code_llm_only_threshold`
- Evidence is ambiguous or incomplete
