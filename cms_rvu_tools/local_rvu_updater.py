#!/usr/bin/env python3
"""
Local RVU Data Updater for IP Coding Knowledge Base

This script updates the IP coding JSON from a local CSV file containing
CMS RVU data. This is useful when:
- Network access to CMS is restricted
- You have a pre-downloaded or custom RVU dataset
- You want to use MACs locality-adjusted values

Usage:
    python local_rvu_updater.py update --input ip_coding.json --rvu-csv cms_rvus.csv --output ip_coding_updated.json
    python local_rvu_updater.py update --input ip_coding.json --rvu-csv cms_rvus.csv --family bronchoscopy
    python local_rvu_updater.py validate --input ip_coding.json --rvu-csv cms_rvus.csv --strict

CSV Format (matches CMS PFS export):
    HCPCS,MOD,DESCRIPTION,WORK_RVU,NON_FAC_PE_RVU,FAC_PE_RVU,MP_RVU,NON_FAC_TOTAL,FAC_TOTAL,GLOB_DAYS,MULT_PROC,STATUS

Author: IP Coding Assistant
Version: 1.1
"""

import csv
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Set


# IP-relevant CPT code sets organized by family
IP_CPT_FAMILIES = {
    "bronchoscopy": [
        "31622", "31623", "31624", "31625", "31626", "31627", "31628", "31629",
        "31630", "31631", "31632", "31633", "31634", "31635", "31636", "31637",
        "31638", "31640", "31641", "31645", "31646", "31647", "31648", "31649",
        "31651", "31652", "31653", "31654", "31660", "31661",
    ],
    "pleural": [
        "32408", "32550", "32551", "32552", "32553", "32554", "32555", "32556", "32557",
        "32560", "32561", "32562",
    ],
    "thoracoscopy": [
        "32601", "32604", "32606", "32607", "32608", "32609",
        "32650", "32651", "32652", "32653", "32654", "32656", "32657", "32666", "32669",
    ],
    "sedation": [
        "99151", "99152", "99153", "99155", "99156", "99157",
    ],
    "em_outpatient": [
        "99202", "99203", "99204", "99205",
        "99211", "99212", "99213", "99214", "99215",
    ],
    "em_inpatient": [
        "99221", "99222", "99223",
        "99231", "99232", "99233",
        "99238", "99239",
    ],
    "em_ed": [
        "99281", "99282", "99283", "99284", "99285",
    ],
    "critical_care": [
        "99291", "99292",
    ],
    "imaging": [
        "71045", "71046", "76942",
    ],
}

# Flatten to single set for backward compatibility
IP_CPT_CODES = set()
for codes in IP_CPT_FAMILIES.values():
    IP_CPT_CODES.update(codes)


def get_codes_for_families(families: List[str]) -> Set[str]:
    """Get CPT codes for specified families."""
    codes = set()
    for family in families:
        family_lower = family.lower().replace("-", "_").replace(" ", "_")
        if family_lower in IP_CPT_FAMILIES:
            codes.update(IP_CPT_FAMILIES[family_lower])
        elif family_lower == "em":
            # Convenience alias for all E/M codes
            codes.update(IP_CPT_FAMILIES["em_outpatient"])
            codes.update(IP_CPT_FAMILIES["em_inpatient"])
            codes.update(IP_CPT_FAMILIES["em_ed"])
            codes.update(IP_CPT_FAMILIES["critical_care"])
        elif family_lower == "airway":
            # Convenience alias for bronchoscopy
            codes.update(IP_CPT_FAMILIES["bronchoscopy"])
        else:
            print(f"Warning: Unknown family '{family}'. Available: {', '.join(IP_CPT_FAMILIES.keys())}")
    return codes


@dataclass
class RVUData:
    """RVU data for a single CPT code."""
    hcpcs: str
    description: str = ""
    work_rvu: Optional[float] = None
    nonfac_pe_rvu: Optional[float] = None
    fac_pe_rvu: Optional[float] = None
    mp_rvu: Optional[float] = None
    nonfac_total: Optional[float] = None
    fac_total: Optional[float] = None
    global_days: str = ""
    mult_proc: int = 0
    status: str = ""
    conversion_factor: float = 32.7442
    
    @property
    def fac_payment(self) -> Optional[int]:
        if self.fac_total:
            return int(round(self.fac_total * self.conversion_factor))
        return None
    
    @property
    def nonfac_payment(self) -> Optional[int]:
        if self.nonfac_total:
            return int(round(self.nonfac_total * self.conversion_factor))
        return None
    
    @property
    def is_add_on(self) -> bool:
        """Add-on codes identified by Global days = ZZZ."""
        return self.global_days == "ZZZ"


def parse_float(val: str) -> Optional[float]:
    """Safely parse a float value."""
    if not val or val.strip() in ("", "NA", "N/A", "-"):
        return None
    try:
        return float(val.strip())
    except ValueError:
        return None


def parse_int(val: str) -> int:
    """Safely parse an integer value."""
    if not val or val.strip() in ("", "NA", "N/A", "-"):
        return 0
    try:
        return int(val.strip())
    except ValueError:
        return 0


# Flexible column name mapping (CMS files vary in naming)
COLUMN_MAPPINGS = {
    "hcpcs": ["HCPCS", "HCPCS_CD", "CPT", "CODE", "PROCEDURE_CODE"],
    "description": ["DESCRIPTION", "DESC", "SHORT_DESC", "MOD_DESC"],
    "work_rvu": ["WORK_RVU", "WORK RVU", "WRVU", "WORK"],
    "nonfac_pe_rvu": ["NON_FAC_PE_RVU", "NONFAC_PE", "PE_RVU_NF", "PRACTICE_EXPENSE_RVU_NONFACILITY"],
    "fac_pe_rvu": ["FAC_PE_RVU", "FAC_PE", "PE_RVU_F", "PRACTICE_EXPENSE_RVU_FACILITY"],
    "mp_rvu": ["MP_RVU", "MP", "MALPRACTICE_RVU", "PLI_RVU"],
    "nonfac_total": ["NON_FAC_TOTAL", "NONFAC_TOTAL", "TOTAL_NONFACILITY", "CONV_NF"],
    "fac_total": ["FAC_TOTAL", "FACILITY_TOTAL", "TOTAL_FACILITY", "CONV_F"],
    "global_days": ["GLOB_DAYS", "GLOBAL", "GLOBAL_DAYS", "GLOB"],
    "mult_proc": ["MULT_PROC", "MULT_SURG", "MULTIPLE_PROCEDURE"],
    "status": ["STATUS", "STATUS_CODE", "STAT"]
}


def find_column(headers: List[str], field: str) -> Optional[int]:
    """Find the column index for a field using flexible mapping."""
    possible_names = COLUMN_MAPPINGS.get(field, [field.upper()])
    headers_upper = [h.upper().strip() for h in headers]
    
    for name in possible_names:
        if name in headers_upper:
            return headers_upper.index(name)
    return None


def load_rvu_csv(csv_path: str, conversion_factor: float = 32.7442, 
                 code_filter: Optional[Set[str]] = None) -> Dict[str, RVUData]:
    """Load RVU data from a CSV file."""
    if code_filter is None:
        code_filter = IP_CPT_CODES
    
    rvu_data = {}
    
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        headers = next(reader)
        
        col_idx = {}
        for field in COLUMN_MAPPINGS.keys():
            idx = find_column(headers, field)
            if idx is not None:
                col_idx[field] = idx
        
        if "hcpcs" not in col_idx:
            raise ValueError(f"Cannot find HCPCS/CPT column in CSV. Headers: {headers}")
        
        for row in reader:
            if len(row) <= col_idx["hcpcs"]:
                continue
            
            hcpcs = row[col_idx["hcpcs"]].strip().lstrip("0")
            
            if code_filter and hcpcs not in code_filter:
                continue
            
            rvu = RVUData(
                hcpcs=hcpcs,
                description=row[col_idx["description"]] if "description" in col_idx else "",
                work_rvu=parse_float(row[col_idx["work_rvu"]]) if "work_rvu" in col_idx else None,
                nonfac_pe_rvu=parse_float(row[col_idx["nonfac_pe_rvu"]]) if "nonfac_pe_rvu" in col_idx else None,
                fac_pe_rvu=parse_float(row[col_idx["fac_pe_rvu"]]) if "fac_pe_rvu" in col_idx else None,
                mp_rvu=parse_float(row[col_idx["mp_rvu"]]) if "mp_rvu" in col_idx else None,
                nonfac_total=parse_float(row[col_idx["nonfac_total"]]) if "nonfac_total" in col_idx else None,
                fac_total=parse_float(row[col_idx["fac_total"]]) if "fac_total" in col_idx else None,
                global_days=row[col_idx["global_days"]].strip() if "global_days" in col_idx else "",
                mult_proc=parse_int(row[col_idx["mult_proc"]]) if "mult_proc" in col_idx else 0,
                status=row[col_idx["status"]].strip() if "status" in col_idx else "",
                conversion_factor=conversion_factor
            )
            
            rvu_data[hcpcs] = rvu
    
    return rvu_data


def categorize_code(hcpcs: str) -> str:
    """Determine the category for a CPT code."""
    for family, codes in IP_CPT_FAMILIES.items():
        if hcpcs in codes:
            category_map = {
                "bronchoscopy": "bronchoscopy",
                "pleural": "pleural",
                "thoracoscopy": "thoracoscopy",
                "sedation": "sedation",
                "em_outpatient": "em",
                "em_inpatient": "em",
                "em_ed": "em",
                "critical_care": "em",
                "imaging": "imaging",
            }
            return category_map.get(family, "other")
    return "other"


def update_json_with_rvus(
    input_path: str,
    rvu_data: Dict[str, RVUData],
    output_path: str,
    source: str = "CMS PFS",
    families: Optional[List[str]] = None
) -> dict:
    """Update the IP coding JSON with RVU data."""
    with open(input_path, 'r') as f:
        data = json.load(f)
    
    summary = {
        "codes_updated": [],
        "codes_not_in_csv": [],
        "families_updated": families or list(IP_CPT_FAMILIES.keys())
    }
    
    if families:
        codes_to_update = get_codes_for_families(families)
    else:
        codes_to_update = IP_CPT_CODES
    
    # Update version
    old_version = data.get("version", "2.0")
    parts = old_version.split(".")
    new_minor = int(parts[1]) + 1 if len(parts) > 1 else 1
    data["version"] = f"{parts[0]}.{new_minor}"
    
    data["metadata"]["label"] = f"ip_coding_billing.v{data['version']}"
    data["metadata"]["updated_on"] = datetime.now().strftime("%Y-%m-%d")
    
    if "changelog" not in data["metadata"]:
        data["metadata"]["changelog"] = []
    
    family_str = ", ".join(families) if families else "all"
    data["metadata"]["changelog"].insert(0, 
        f"v{data['version']}: Updated RVU values from {source} on {datetime.now().strftime('%Y-%m-%d')} (families: {family_str})"
    )
    
    if "cms_rvus" not in data:
        data["cms_rvus"] = {
            "_metadata": {
                "source": source,
                "conversion_factor": 32.7442,
                "retrieved": datetime.now().strftime("%Y-%m-%d")
            }
        }
    
    categories = {"bronchoscopy": {}, "pleural": {}, "thoracoscopy": {}, "sedation": {}, "em": {}, "imaging": {}}
    
    for hcpcs, rvu in rvu_data.items():
        if hcpcs not in codes_to_update:
            continue
            
        category = categorize_code(hcpcs)
        if category not in categories:
            categories[category] = {}
        
        code_entry = {
            "description": rvu.description,
            "work_rvu": rvu.work_rvu,
            "facility_pe_rvu": rvu.fac_pe_rvu,
            "nonfacility_pe_rvu": rvu.nonfac_pe_rvu,
            "mp_rvu": rvu.mp_rvu,
            "total_facility_rvu": rvu.fac_total,
            "total_nonfacility_rvu": rvu.nonfac_total,
            "mpfs_facility_payment": rvu.fac_payment,
            "mpfs_nonfacility_payment": rvu.nonfac_payment,
            "global_days": rvu.global_days,
            "mult_proc_indicator": rvu.mult_proc,
            "status_code": rvu.status,
            "is_add_on": rvu.is_add_on
        }
        
        categories[category][hcpcs] = code_entry
        summary["codes_updated"].append(hcpcs)
    
    for cat_name, cat_codes in categories.items():
        if cat_codes:
            if cat_name not in data["cms_rvus"]:
                data["cms_rvus"][cat_name] = {}
            data["cms_rvus"][cat_name].update(cat_codes)
    
    for schedule_name, schedule_data in data.get("fee_schedules", {}).items():
        codes = schedule_data.get("codes", {})
        for code in list(codes.keys()):
            lookup_code = code.lstrip("+")
            if lookup_code not in codes_to_update:
                continue
            if lookup_code in rvu_data:
                rvu = rvu_data[lookup_code]
                if rvu.work_rvu is not None:
                    codes[code]["work_rvu"] = rvu.work_rvu
                if rvu.fac_total is not None:
                    codes[code]["total_facility_rvu"] = rvu.fac_total
                if rvu.nonfac_total is not None:
                    codes[code]["total_nonfacility_rvu"] = rvu.nonfac_total
                if rvu.fac_payment is not None:
                    codes[code]["mpfs_facility_payment"] = rvu.fac_payment
                if rvu.nonfac_payment is not None:
                    codes[code]["mpfs_nonfacility_payment"] = rvu.nonfac_payment
            else:
                summary["codes_not_in_csv"].append(code)
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    return summary


def validate_csv_against_json(
    json_path: str, 
    rvu_data: Dict[str, RVUData],
    threshold: float = 0.1,
    families: Optional[List[str]] = None
) -> List[dict]:
    """Validate CSV data against JSON and return discrepancies."""
    with open(json_path, 'r') as f:
        json_data = json.load(f)
    
    if families:
        codes_to_validate = get_codes_for_families(families)
    else:
        codes_to_validate = IP_CPT_CODES
    
    issues = []
    
    for schedule_name, schedule_data in json_data.get("fee_schedules", {}).items():
        for code, code_data in schedule_data.get("codes", {}).items():
            lookup_code = code.lstrip("+")
            
            if codes_to_validate and lookup_code not in codes_to_validate:
                continue
            
            if lookup_code not in rvu_data:
                issues.append({
                    "code": code,
                    "section": f"fee_schedules.{schedule_name}",
                    "issue": "not_in_csv",
                    "message": f"{code} not found in CSV"
                })
                continue
            
            rvu = rvu_data[lookup_code]
            
            json_work = code_data.get("work_rvu")
            if json_work is not None and rvu.work_rvu is not None:
                diff = abs(json_work - rvu.work_rvu)
                if diff > threshold:
                    issues.append({
                        "code": code,
                        "section": f"fee_schedules.{schedule_name}",
                        "field": "work_rvu",
                        "issue": "discrepancy",
                        "json_value": json_work,
                        "csv_value": rvu.work_rvu,
                        "diff": diff,
                        "message": f"{code} work_rvu: JSON={json_work}, CSV={rvu.work_rvu}, diff={diff:.2f}"
                    })
            
            json_fac = code_data.get("total_facility_rvu")
            if json_fac is not None and rvu.fac_total is not None:
                diff = abs(json_fac - rvu.fac_total)
                if diff > threshold:
                    issues.append({
                        "code": code,
                        "section": f"fee_schedules.{schedule_name}",
                        "field": "total_facility_rvu",
                        "issue": "discrepancy",
                        "json_value": json_fac,
                        "csv_value": rvu.fac_total,
                        "diff": diff,
                        "message": f"{code} total_facility_rvu: JSON={json_fac}, CSV={rvu.fac_total}, diff={diff:.2f}"
                    })
    
    for cat_name, cat_codes in json_data.get("cms_rvus", {}).items():
        if cat_name.startswith("_"):
            continue
        if not isinstance(cat_codes, dict):
            continue
        
        for code, code_data in cat_codes.items():
            if codes_to_validate and code not in codes_to_validate:
                continue
            
            if code not in rvu_data:
                continue
            
            rvu = rvu_data[code]
            
            json_work = code_data.get("work_rvu")
            if json_work is not None and rvu.work_rvu is not None:
                diff = abs(json_work - rvu.work_rvu)
                if diff > threshold:
                    issues.append({
                        "code": code,
                        "section": f"cms_rvus.{cat_name}",
                        "field": "work_rvu",
                        "issue": "discrepancy",
                        "json_value": json_work,
                        "csv_value": rvu.work_rvu,
                        "diff": diff,
                        "message": f"{code} work_rvu: JSON={json_work}, CSV={rvu.work_rvu}, diff={diff:.2f}"
                    })
    
    return issues


def generate_template_csv(output_path: str, families: Optional[List[str]] = None):
    """Generate a template CSV file with IP CPT codes."""
    if families:
        codes = get_codes_for_families(families)
    else:
        codes = IP_CPT_CODES
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            "HCPCS", "DESCRIPTION", "WORK_RVU", "NON_FAC_PE_RVU", "FAC_PE_RVU",
            "MP_RVU", "NON_FAC_TOTAL", "FAC_TOTAL", "GLOB_DAYS", "MULT_PROC", "STATUS"
        ])
        
        for code in sorted(codes):
            writer.writerow([code, "", "", "", "", "", "", "", "", "", ""])
    
    print(f"Template CSV created: {output_path}")
    print(f"Contains {len(codes)} CPT codes")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Update IP coding JSON with RVU data from a local CSV file"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update JSON with RVU data")
    update_parser.add_argument("--input", "-i", required=True, help="Input IP coding JSON file")
    update_parser.add_argument("--rvu-csv", "-r", required=True, help="CSV file with RVU data")
    update_parser.add_argument("--output", "-o", help="Output JSON file (default: input_updated.json)")
    update_parser.add_argument("--cf", type=float, default=32.7442, 
                              help="Medicare conversion factor. Default: 32.7442 (CY 2025 national unadjusted). "
                                   "This is the CF from the CMS Physician Fee Schedule Final Rule. "
                                   "For locality-adjusted values, use your MAC's GPCI-adjusted CF.")
    update_parser.add_argument("--source", "-s", default="CMS PFS", help="Source description for metadata")
    update_parser.add_argument("--family", "-f", action="append", dest="families",
                              help="Code family to update (can specify multiple). Options: bronchoscopy, pleural, thoracoscopy, sedation, em_outpatient, em_inpatient, em_ed, critical_care, imaging, em (all E/M), airway (bronchoscopy)")
    
    # Template command
    template_parser = subparsers.add_parser("template", help="Generate template CSV")
    template_parser.add_argument("--output", "-o", default="ip_rvu_template.csv", help="Output CSV file")
    template_parser.add_argument("--family", "-f", action="append", dest="families",
                                help="Code family to include (can specify multiple)")
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate CSV against JSON")
    validate_parser.add_argument("--input", "-i", required=True, help="Input IP coding JSON file")
    validate_parser.add_argument("--rvu-csv", "-r", required=True, help="CSV file with RVU data")
    validate_parser.add_argument("--threshold", "-t", type=float, default=0.1, 
                                help="RVU difference threshold to report (default: 0.1)")
    validate_parser.add_argument("--family", "-f", action="append", dest="families",
                                help="Code family to validate (can specify multiple)")
    validate_parser.add_argument("--strict", action="store_true",
                                help="Exit with non-zero code if any discrepancies found (for CI)")
    validate_parser.add_argument("--json-output", help="Write validation results to JSON file")
    
    # List command
    list_parser = subparsers.add_parser("list-families", help="List available code families")
    
    args = parser.parse_args()
    
    if args.command == "list-families":
        print("Available code families:")
        for family, codes in sorted(IP_CPT_FAMILIES.items()):
            print(f"  {family}: {len(codes)} codes ({codes[0]}-{codes[-1]})")
        print("\nAliases:")
        print("  em: all E/M codes (em_outpatient + em_inpatient + em_ed + critical_care)")
        print("  airway: bronchoscopy codes")
    
    elif args.command == "template":
        generate_template_csv(args.output, args.families)
        
    elif args.command == "update":
        output = args.output or args.input.replace(".json", "_updated.json")
        
        code_filter = None
        if args.families:
            code_filter = get_codes_for_families(args.families)
            print(f"Filtering to families: {', '.join(args.families)} ({len(code_filter)} codes)")
        
        print(f"Loading RVU data from {args.rvu_csv}...")
        rvu_data = load_rvu_csv(args.rvu_csv, args.cf, code_filter)
        print(f"Loaded {len(rvu_data)} codes")
        
        print(f"Updating {args.input}...")
        summary = update_json_with_rvus(args.input, rvu_data, output, args.source, args.families)
        
        print(f"\nUpdate complete!")
        print(f"  - Codes updated: {len(summary['codes_updated'])}")
        print(f"  - Codes not in CSV: {len(summary['codes_not_in_csv'])}")
        print(f"  - Output: {output}")
        
    elif args.command == "validate":
        code_filter = None
        if args.families:
            code_filter = get_codes_for_families(args.families)
            print(f"Validating families: {', '.join(args.families)} ({len(code_filter)} codes)")
        
        print(f"Loading RVU data from {args.rvu_csv}...")
        rvu_data = load_rvu_csv(args.rvu_csv, code_filter=code_filter)
        print(f"Loaded {len(rvu_data)} codes")
        
        print(f"\nValidating against {args.input}...")
        issues = validate_csv_against_json(args.input, rvu_data, args.threshold, args.families)
        
        print(f"\nValidation Results:")
        if issues:
            print(f"Found {len(issues)} discrepancies (threshold > {args.threshold} RVU):")
            for issue in issues[:30]:
                print(f"  {issue['message']}")
            if len(issues) > 30:
                print(f"  ... and {len(issues) - 30} more")
            
            if args.json_output:
                with open(args.json_output, 'w') as f:
                    json.dump({"issues": issues, "count": len(issues)}, f, indent=2)
                print(f"\nDetailed results written to: {args.json_output}")
            
            if args.strict:
                print(f"\n[STRICT MODE] Exiting with code 1 due to {len(issues)} discrepancies")
                sys.exit(1)
        else:
            print("  No discrepancies found!")
            if args.json_output:
                with open(args.json_output, 'w') as f:
                    json.dump({"issues": [], "count": 0}, f, indent=2)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
