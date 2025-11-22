# Registry self-correction for patient_mrn

## Current instruction
Patient medical record number or clearly labeled patient ID. Prefer explicit MRN/ID labels (e.g., "MRN: 3847592", "ID: MR4729384"). Do not return dates, accession numbers, or phone-like numbers. Preserve the ID format; strip labels if included. If no MRN/ID documented, return null.

## Suggested updates
### updated_instruction
Return the patient's medical record number (MRN) or clearly labeled patient ID.

Selection rules:
- Prefer fields explicitly labeled as a patient identifier, such as:
  - "MRN", "Medical Record Number", "Pt MRN"
  - "ID", "Patient ID", "Pt ID", "Acct ID" when clearly referring to the patient.
- When multiple candidate IDs exist, choose in this order of preference:
  1) Explicit MRN label (e.g., "MRN: 3847592").
  2) Patient ID/ID next to the patient name or demographic header (e.g., "Patient: Smith, John | ID: MR4729384 | Age: 72").
  3) Other clearly patient-related ID fields if they are in the demographics/header section.
- Ignore and do NOT return:
  - Dates, times, phone-like numbers, fax numbers.
  - Accession numbers, specimen numbers, order numbers, encounter numbers, visit numbers, room/bed numbers.
  - Numbers/IDs attached to lab tests, imaging, pathology, or devices (e.g., scope serials, equipment IDs).

Formatting rules:
- Return only the ID value, without any label or punctuation, exactly as written (preserve case, letters, and leading zeros).
- If the ID contains spaces or dashes as part of its format, preserve them.
- If no MRN or patient ID is documented, return null.

Examples:
- "Patient: Moore, Christopher | ID: MR4729384 | Age: 72" → mr4729384
- "MRN: 000123456" → 000123456
- "Patient ID: ABC-99-123" → ABC-99-123
- "Accession #: 22-12345" with no other ID → null

### python_postprocessing_rules
import re

def normalize_patient_mrn(text: str | None) -> str | None:
    if text is None:
        return None
    raw = text.strip()
    if not raw:
        return None

    # Remove any surrounding quotes or trailing punctuation commonly left around IDs
    raw = raw.strip().strip('"\'').strip(',:;')

    # Reject if it looks obviously like a date (very rough safeguard)
    date_like = re.compile(r"^\d{1,2}[\-/]\d{1,2}[\-/]\d{2,4}$")
    if date_like.match(raw):
        return None

    # Reject obvious phone-like patterns (7–15 digits with optional separators)
    phone_like = re.compile(r"^\+?\d[\d\-\s()]{6,}$")
    if phone_like.match(raw) and not re.search(r"[A-Za-z]", raw):
        return None

    # If model accidentally returns with label (e.g., "MRN: 12345"), strip common labels
    m = re.search(r"(?:MRN|Medical Record Number|Patient ID|Pt ID|ID)\s*[:#-]?\s*(.+)$", raw, re.IGNORECASE)
    if m:
        candidate = m.group(1).strip()
    else:
        candidate = raw

    # Final clean of trailing punctuation
    candidate = candidate.strip().strip(',:;')

    # If after cleaning nothing remains, treat as null
    if not candidate:
        return None

    return candidate

### comments
Clarified priority to use the explicitly labeled MRN or patient ID that appears in the patient header, especially an 'ID' located next to the patient name and demographics, to avoid selecting unrelated numeric fields. Strengthened negative rules against accession, specimen, and other non-patient IDs. Added explicit examples including the failing case, and provided postprocessing to strip leftover labels and filter out date/phone-like outputs while preserving case and formatting of valid IDs.

