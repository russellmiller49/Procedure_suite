# Narrative annotations design notes

Use this reference when the bundle contract needs a new narrative preservation channel.

## Good annotation categories

- `indication`
- `intraop_event`
- `complication`
- `plan`
- `dose_detail`
- `outcome_detail`
- `device_change`
- `finding_detail`

## Good candidate source patterns

- `switched from X to Y`
- `converted to`
- `removed and replaced`
- `migrated`
- `unable to`
- `desaturated to`
- `opened from X% to Y%`

## Design principles

- Preserve clinically important source text that otherwise has no home.
- Keep the extracted text near-verbatim where feasible.
- Store a source span whenever possible.
- Let templates decide how to present the detail; do not force every annotation into a structured field.
