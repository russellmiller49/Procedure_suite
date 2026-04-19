# Evidence invariants for Procedure Suite coding

Use these rules when changing CPT traceability.

## Core invariants

- A primary evidence span must not fall inside a header or menu code block.
- A CPT should be anchored to narrative or structured clinical evidence whenever possible.
- Header/menu numerals may be preserved as hints when the deterministic path explicitly expects them, but they should not masquerade as narrative evidence.
- If support is indirect, label it honestly as implied or hint-backed support.

## Common failure pattern

A header such as `PROCEDURE: 31646` leaks into the billing output as the primary evidence span. This hides disagreements between the note narrative and the menu/header code list and makes audit review look stronger than the source text supports.

## Preferred fix shape

- Separate `header_code_hint` or equivalent from narrative `code_evidence`.
- Veto header/menu spans during final evidence anchoring.
- Update guarded deterministic rules to consult the hint channel directly where needed.
- Add a test that proves header/menu numerals are not used as primary note spans.
