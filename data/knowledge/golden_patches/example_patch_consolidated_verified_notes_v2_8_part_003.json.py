import json
import datetime
from pathlib import Path

# Get the script's directory and resolve paths relative to it
SCRIPT_DIR = Path(__file__).parent.parent  # Goes up from golden_patches/ to knowledge/

KB_PATH = SCRIPT_DIR / "ip_coding_billing.v2_7.json"
INPUT_PATH = SCRIPT_DIR / "golden_extractions" / "consolidated_verified_notes_v2_8_part_003.json"
OUTPUT_PATH = SCRIPT_DIR / "golden_extractions" / "consolidated_verified_notes_v2_8_part_003.patched.json"



def build_rvu_lookup(kb: dict) -> dict:
    """
    Combine RVUs from airway, pleural, and sedation/E&M sections into a single dict.

    Returns: {code_str: {"work": float, "pe": float, "mp": float}}
    """
    combined = {}

    for section in ["rvus", "rvus_pleural", "rvus_sedation_em"]:
        if section not in kb:
            continue
        for code, vals in kb[section].items():
            if code.startswith("_"):
                continue
            # Expect keys work / pe / mp
            combined[code] = {
                "work": float(vals["work"]),
                "pe": float(vals["pe"]),
                "mp": float(vals["mp"]),
            }

    return combined


def build_fee_lookup(kb: dict) -> dict:
    """
    Pull fee schedule info (description, total_facility_rvu, mpfs_facility_payment)
    from airway + pleural + Noah-core schedules.
    """
    fee = {}
    schedules = [
        "physician_2025_airway",
        "physician_2025_pleural",
        "physician_2025_noah_core",
    ]
    for sched_name in schedules:
        sched = kb["fee_schedules"].get(sched_name)
        if not sched:
            continue
        codes = sched["codes"]
        for code, vals in codes.items():
            if code.startswith("_"):
                continue
            # First schedule wins if duplicates
            fee.setdefault(code, vals)
    return fee


def get_rvu_for_code(code_int: int, rvus: dict, fees: dict, conversion_factor: float):
    """
    Given an integer CPT code (e.g. 31627), return:
      billing_code_str (with + for add-ons where appropriate),
      work, pe, mp, total_rvu, total_facility_rvu, mpfs_facility_payment, description
    """
    num = f"{code_int:05d}"   # "31627"
    plus = f"+{num}"

    # Decide whether this is an add-on code based on the RVU lookup
    if plus in rvus:
        key = plus
    elif num in rvus:
        key = num
    else:
        # Fallback: if fee schedule only has plus or plain, use that
        if plus in fees:
            key = plus
        else:
            key = num

    work = pe = mp = total_rvu = None
    if key in rvus:
        work = rvus[key]["work"]
        pe = rvus[key]["pe"]
        mp = rvus[key]["mp"]
        total_rvu = work + pe + mp

    total_facility_rvu = None
    mpfs_payment = None
    description = None

    # Try fee schedule with key, then plain, then plus
    for fk in (key, num, plus):
        if fk in fees:
            fvals = fees[fk]
            description = fvals.get("description")
            total_facility_rvu = fvals.get("total_facility_rvu")
            mpfs_payment = fvals.get("mpfs_facility_payment")
            break

    # If fee schedule doesn’t have total_facility_rvu, fall back to RVU sum
    if total_facility_rvu is None and total_rvu is not None:
        total_facility_rvu = total_rvu

    # If payment missing but we have total_facility_rvu, approximate
    if mpfs_payment is None and total_facility_rvu is not None:
        mpfs_payment = round(total_facility_rvu * conversion_factor)

    return key, work, pe, mp, total_rvu, total_facility_rvu, mpfs_payment, description


def populate_billing_for_note(note: dict, rvus: dict, fees: dict, conversion_factor: float):
    """
    Mutates a single note dict in-place:
    - sets registry_entry["billing"]
    - updates patch_metadata
    """
    cpt_list = note.get("cpt_codes") or []
    registry_entry = note["registry_entry"]

    billing_cpts = []
    total_work = total_pe = total_mp = total_fac = 0.0
    used_codes_for_log = []

    for code_int in cpt_list:
        (
            billing_code,
            work,
            pe,
            mp,
            total_rvu,
            total_facility_rvu,
            _payment,
            description,
        ) = get_rvu_for_code(code_int, rvus, fees, conversion_factor)

        used_codes_for_log.append(billing_code)

        billing_cpts.append(
            {
                "code": billing_code,
                "description": description,
                "modifier": None,
                "modifiers": None,
                "units": 1,
            }
        )

        if work is not None:
            total_work += work
        if pe is not None:
            total_pe += pe
        if mp is not None:
            total_mp += mp
        if total_facility_rvu is not None:
            total_fac += total_facility_rvu

    billing_obj = {
        "cpt_codes": billing_cpts,
        "icd10_codes": None,
        "total_rvu": round(total_fac, 2) if total_fac else None,
        "work_rvu": round(total_work, 2) if total_work else None,
        "practice_expense_rvu": round(total_pe, 2) if total_pe else None,
        "malpractice_rvu": round(total_mp, 2) if total_mp else None,
    }

    registry_entry["billing"] = billing_obj

    # Update patch_metadata in the same style as part_001
    pm = note.get("patch_metadata") or {}
    pm["patched"] = True
    pm["patch_version"] = "1.1.0"
    pm["patch_date"] = datetime.datetime.now().isoformat()

    changes = list(pm.get("changes") or [])
    changes.append(
        (
            "Populated registry_entry.billing from ip_coding_billing.v2_7 for CPT codes "
            f"{', '.join(used_codes_for_log)}; "
            f"total_work_rvu={billing_obj['work_rvu']}, "
            f"total_rvu={billing_obj['total_rvu']} (facility)."
        )
    )
    pm["changes"] = changes

    if "warnings" not in pm or pm["warnings"] is None:
        pm["warnings"] = []

    note["patch_metadata"] = pm


def main():
    kb = json.loads(KB_PATH.read_text())
    data = json.loads(INPUT_PATH.read_text())

    rvus = build_rvu_lookup(kb)
    fees = build_fee_lookup(kb)
    conversion_factor = float(kb["cms_rvus"]["_conversion_factor"])

    for note in data:
        populate_billing_for_note(note, rvus, fees, conversion_factor)

    OUTPUT_PATH.write_text(json.dumps(data, indent=2))
    print(f"Wrote patched file to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
