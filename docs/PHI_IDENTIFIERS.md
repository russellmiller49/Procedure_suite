# PHI Identifiers (HIPAA Safe Harbor) — Quick Reference

Procedure Suite stores **scrubbed-only** text when Registry Runs persistence is enabled.
Before saving anything, ensure the note contains **none** of the patient identifiers below.

## HIPAA Safe Harbor — 18 Identifiers

1. **Names** (patient or family member names).
2. **Geographic subdivisions smaller than a state**, including:
   - street address, city, county, precinct
   - ZIP code (except allowed 3-digit ZIP under HIPAA rules)
3. **All elements of dates (except year)** directly related to an individual, including:
   - date of birth, admission/discharge dates, date of death
   - ages **> 89** (and any date elements indicative of such age)
4. **Telephone numbers**
5. **Fax numbers**
6. **Email addresses**
7. **Social Security numbers**
8. **Medical record numbers (MRN)**
9. **Health plan beneficiary numbers**
10. **Account numbers**
11. **Certificate/license numbers**
12. **Vehicle identifiers and serial numbers**, including license plates
13. **Device identifiers and serial numbers**
14. **Web URLs**
15. **IP addresses**
16. **Biometric identifiers**, including finger and voice prints
17. **Full-face photos** and any comparable images
18. **Any other unique identifying number, characteristic, or code**

## Common Notes for Procedure Suite

- **Provider/physician names** are generally **not patient PHI** and may appear in the note (e.g., attending, endoscopist).
  If a name is ambiguous (could be the patient), treat it as PHI and redact it.
- **Device model names/numbers** (e.g., “Olympus BF‑1TQ190”) are typically acceptable.
  **Unique device serial numbers** should be treated as PHI identifiers and redacted.
- When in doubt: **redact** and re-run the pipeline.

