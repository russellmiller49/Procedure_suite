from __future__ import annotations

from pathlib import Path
from typing import Optional, Iterable, Any, Dict
import csv
from decimal import Decimal

from proc_autocode.rvu.rvu_parser import CMSRVUParser, RVURecord
from proc_autocode.ip_kb.ip_kb import IPCodingKnowledgeBase


def export_rvu_subset(
    cms_rvu_file: Path,
    ip_json_file: Path,
    output_csv: Path,
) -> None:
    """
    Build a CSV containing RVU data (in CMS format) for all CPT/HCPCS
    referenced in ip_coding_billing.

    cms_rvu_file:
        - Either the big CMS fixed-width PPRRVU file (.txt)
        - OR a CSV in the same column format as sample_rvu_2025.csv
    """
    kb = IPCodingKnowledgeBase(ip_json_file)
    parser = CMSRVUParser()

    # Heuristic: choose parser based on file extension
    if cms_rvu_file.suffix.lower() == ".csv":
        parsed = parser.parse_csv_file(cms_rvu_file)
    else:
        parsed = parser.parse_file(cms_rvu_file)

    print(f"Loaded {parsed} CMS RVU records from {cms_rvu_file}")

    target_codes = kb.all_relevant_cpt_codes()
    print(f"Found {len(target_codes)} unique CPT/HCPCS codes in ip_coding_billing")

    # We will write a CSV compatible with CMSRVUParser.parse_csv_file
    fieldnames = [
        "HCPCS",
        "MOD",
        "DESCRIPTION",
        "STATUS CODE",
        "WORK RVU",
        "NON-FAC PE RVU",
        "FACILITY PE RVU",
        "MP RVU",
        "NON-FAC TOTAL",
        "FACILITY TOTAL",
        "PCTC IND",
        "GLOB DAYS",
        "MULT PROC",
        "BILAT SURG",
        "ASST SURG",
        "CO-SURG",
        "TEAM SURG",
        "CONV FACTOR",
    ]

    missing: list[str] = []
    
    # Ensure output directory exists
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    with output_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for cpt in sorted(target_codes):
            rec = parser.get_record(cpt)
            
            if not rec:
                # Attempt to synthesize from KB
                rec = _synthesize_record(cpt, kb)
            
            if not rec:
                missing.append(cpt)
                continue

            writer.writerow(
                {
                    "HCPCS": rec.hcpcs_code,
                    "MOD": rec.modifier,
                    "DESCRIPTION": rec.description,
                    "STATUS CODE": rec.status_code,
                    "WORK RVU": rec.work_rvu,
                    "NON-FAC PE RVU": rec.non_fac_pe_rvu,
                    "FACILITY PE RVU": rec.fac_pe_rvu,
                    "MP RVU": rec.mp_rvu,
                    "NON-FAC TOTAL": rec.total_non_fac_rvu,
                    "FACILITY TOTAL": rec.total_fac_rvu,
                    "PCTC IND": rec.pctc_indicator,
                    "GLOB DAYS": rec.global_surgery,
                    "MULT PROC": rec.mult_proc_indicator,
                    "BILAT SURG": rec.bilateral_surgery,
                    "ASST SURG": rec.assistant_surgery,
                    "CO-SURG": rec.co_surgeons,
                    "TEAM SURG": rec.team_surgery,
                    "CONV FACTOR": rec.conversion_factor,
                }
            )

    print(f"Wrote RVU subset to {output_csv}")
    if missing:
        print("WARNING: CMS RVU record not found (and could not synthesize) for the following codes:")
        print(", ".join(sorted(missing)))


def _synthesize_record(cpt: str, kb: IPCodingKnowledgeBase) -> Optional[RVURecord]:
    """Create a partial RVURecord from knowledge base JSON data"""
    info = kb.get_cpt_info(cpt)
    if not info or not info.rvus:
        return None

    # Get RVUs from JSON
    w = info.rvus.get("work")
    pe = info.rvus.get("pe")
    mp = info.rvus.get("mp")

    if w is None: 
        return None # Minimal requirement

    # Clean input strings/floats
    def to_dec(val):
        return Decimal(str(val)) if val is not None else Decimal('0.00')

    w_dec = to_dec(w)
    pe_dec = to_dec(pe)
    mp_dec = to_dec(mp)
    
    total = w_dec + pe_dec + mp_dec

    # Determine status code
    status = "A" if not info.is_add_on else "A" # Simplified
    
    # Description
    desc = info.description or "Generated Description"

    return RVURecord(
        hcpcs_code=cpt,
        modifier="",
        description=desc[:50], # truncate
        status_code=status,
        work_rvu=w_dec,
        non_fac_pe_rvu=pe_dec, # Assume same for simplicity if not specified
        fac_pe_rvu=pe_dec,
        mp_rvu=mp_dec,
        total_non_fac_rvu=total,
        total_fac_rvu=total,
        pctc_indicator="0",
        global_surgery="000", # Default
        mult_proc_indicator="2", # Standard reduction
        bilateral_surgery="0",
        assistant_surgery="0",
        co_surgeons="0",
        team_surgery="0",
        conversion_factor=Decimal("32.35") # 2025 Standard
    )


if __name__ == "__main__":
    # Example CLI usage; adjust paths to your repo structure
    base = Path(__file__).resolve().parents[2]  # repo root (project root)
    # We use sample_rvu_2025.csv as the "CMS file" since we don't have the full TXT
    cms_file = base / "proc_autocode" / "rvu" / "data" / "sample_rvu_2025.csv"
    ip_json = base / "data" / "knowledge" / "ip_coding_billing.v2_7.json"
    out_csv = base / "proc_autocode" / "rvu" / "data" / "rvu_ip_2025.csv"

    if not cms_file.exists():
        print(f"Error: CMS RVU file not found at {cms_file}")
        # Try looking in data/RVU_files just in case
        alt_cms_file = base / "data" / "RVU_files" / "sample_rvu_2025.csv"
        if alt_cms_file.exists():
             print(f"Found at {alt_cms_file}, using that.")
             cms_file = alt_cms_file
        else:
             exit(1)

    export_rvu_subset(cms_file, ip_json, out_csv)
