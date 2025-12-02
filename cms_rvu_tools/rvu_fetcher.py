#!/usr/bin/env python3
"""
CMS RVU Data Integration Module for Interventional Pulmonology Coding

This module fetches official CMS Physician Fee Schedule RVU data and integrates
it with the IP coding/billing knowledge base, ensuring authoritative values
are used and flagging any discrepancies.

Data Source: CMS Physician Fee Schedule Relative Value Files
https://www.cms.gov/medicare/payment/fee-schedules/physician/pfs-relative-value-files

Author: IP Coding Assistant
Version: 1.0
"""

import json
import os
import re
import zipfile
from dataclasses import dataclass, field, asdict
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Optional
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# Try to import pandas/openpyxl, fall back to csv parsing if not available
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    import csv


# =============================================================================
# Configuration
# =============================================================================

# IP-relevant CPT code families
IP_CPT_CODES = {
    # Bronchoscopy codes
    "bronchoscopy": [
        "31622", "31623", "31624", "31625", "31626", "31627", "31628", "31629",
        "31630", "31631", "31632", "31633", "31634", "31635", "31636", "31637",
        "31638", "31640", "31641", "31645", "31646", "31647", "31648", "31649",
        "31651", "31652", "31653", "31654", "31660", "31661"
    ],
    # Pleural procedures
    "pleural": [
        "32408",  # TTNA
        "32550", "32551", "32552", "32553", "32554", "32555", "32556", "32557",
        "32560", "32561", "32562"
    ],
    # Thoracoscopy
    "thoracoscopy": [
        "32601", "32604", "32606", "32607", "32608", "32609",
        "32650", "32651", "32652", "32653", "32654", "32656", "32657",
        "32666", "32669"
    ],
    # Sedation
    "sedation": [
        "99151", "99152", "99153", "99155", "99156", "99157"
    ],
    # E/M codes commonly used
    "em": [
        "99202", "99203", "99204", "99205",
        "99211", "99212", "99213", "99214", "99215",
        "99221", "99222", "99223",
        "99231", "99232", "99233",
        "99238", "99239",
        "99281", "99282", "99283", "99284", "99285",
        "99291", "99292"
    ],
    # Chest imaging (for bundling reference)
    "imaging": [
        "71045", "71046", "71047", "71048",
        "76942"  # US guidance
    ]
}

# Flatten all codes into a single set
ALL_IP_CODES = set()
for family in IP_CPT_CODES.values():
    ALL_IP_CODES.update(family)

# CMS file URLs (update annually)
CMS_RVU_URLS = {
    "2025": "https://www.cms.gov/files/zip/rvu25a.zip",
    "2024": "https://www.cms.gov/files/zip/rvu24d.zip",
}

# Expected column mappings (CMS changes these slightly year to year)
COLUMN_MAPPINGS = {
    "hcpcs": ["HCPCS", "CPT", "CPT/HCPCS"],
    "modifier": ["MOD", "MODIFIER"],
    "description": ["DESCRIPTION", "DESC", "SHORT DESCRIPTION"],
    "work_rvu": ["WORK RVU", "WORK_RVU", "WRVU"],
    "nonfac_pe_rvu": ["NON-FAC PE RVU", "NON_FAC_PE_RVU", "NFPE", "PE_NONFAC", "TRANSITIONED NON-FACILITY PE RVU"],
    "fac_pe_rvu": ["FAC PE RVU", "FAC_PE_RVU", "FPE", "PE_FAC", "TRANSITIONED FACILITY PE RVU"],
    "mp_rvu": ["MP RVU", "MP_RVU", "PLI RVU", "MALPRACTICE RVU"],
    "nonfac_total": ["NON-FACILITY TOTAL", "NONFAC_TOTAL", "TOTAL_NONFAC"],
    "fac_total": ["FACILITY TOTAL", "FAC_TOTAL", "TOTAL_FAC"],
    "global_days": ["GLOB DAYS", "GLOBAL", "GLOBAL DAYS", "GLOB"],
    "mult_proc": ["MULT PROC", "MULT_PROC", "MPC"],
    "status": ["STATUS CODE", "STATUS", "STAT"],
    "pctc": ["PCTC IND", "PCTC", "PC/TC"]
}


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class RVURecord:
    """Represents a single CPT code's RVU data from CMS."""
    hcpcs: str
    modifier: str = ""
    description: str = ""
    work_rvu: Optional[float] = None
    nonfac_pe_rvu: Optional[float] = None
    fac_pe_rvu: Optional[float] = None
    mp_rvu: Optional[float] = None
    nonfac_total_rvu: Optional[float] = None
    fac_total_rvu: Optional[float] = None
    global_days: str = ""
    mult_proc_indicator: int = 0
    status_code: str = ""
    pctc_indicator: int = 0
    conversion_factor: float = 32.7442  # 2025 CF
    
    @property
    def nonfac_payment(self) -> Optional[float]:
        """Calculate non-facility payment."""
        if self.nonfac_total_rvu is not None:
            return round(self.nonfac_total_rvu * self.conversion_factor, 2)
        return None
    
    @property
    def fac_payment(self) -> Optional[float]:
        """Calculate facility payment."""
        if self.fac_total_rvu is not None:
            return round(self.fac_total_rvu * self.conversion_factor, 2)
        return None
    
    @property
    def is_add_on(self) -> bool:
        """Check if this is an add-on code based on status."""
        return self.status_code == "A" or self.global_days == "ZZZ"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "hcpcs": self.hcpcs,
            "modifier": self.modifier,
            "description": self.description,
            "work_rvu": self.work_rvu,
            "facility_pe_rvu": self.fac_pe_rvu,
            "nonfacility_pe_rvu": self.nonfac_pe_rvu,
            "mp_rvu": self.mp_rvu,
            "total_facility_rvu": self.fac_total_rvu,
            "total_nonfacility_rvu": self.nonfac_total_rvu,
            "mpfs_facility_payment": self.fac_payment,
            "mpfs_nonfacility_payment": self.nonfac_payment,
            "global_days": self.global_days,
            "mult_proc_indicator": self.mult_proc_indicator,
            "status_code": self.status_code,
            "is_add_on": self.is_add_on
        }


@dataclass
class ValidationResult:
    """Result of validating existing data against CMS source."""
    code: str
    field: str
    existing_value: any
    cms_value: any
    difference: Optional[float] = None
    severity: str = "info"  # info, warning, error
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class IntegrationReport:
    """Report of the RVU data integration process."""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    cms_source_year: str = ""
    cms_source_file: str = ""
    conversion_factor: float = 0.0
    total_codes_fetched: int = 0
    ip_codes_extracted: int = 0
    codes_not_found: list = field(default_factory=list)
    validation_issues: list = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "cms_source_year": self.cms_source_year,
            "cms_source_file": self.cms_source_file,
            "conversion_factor": self.conversion_factor,
            "total_codes_fetched": self.total_codes_fetched,
            "ip_codes_extracted": self.ip_codes_extracted,
            "codes_not_found": self.codes_not_found,
            "validation_issues": [v.to_dict() for v in self.validation_issues]
        }


# =============================================================================
# Data Fetching Functions
# =============================================================================

def download_cms_rvu_file(year: str = "2025", cache_dir: str = "./cache") -> Path:
    """
    Download CMS RVU file for the specified year.
    
    Args:
        year: The fee schedule year (e.g., "2025")
        cache_dir: Directory to cache downloaded files
        
    Returns:
        Path to the downloaded/cached file
    """
    cache_path = Path(cache_dir)
    cache_path.mkdir(parents=True, exist_ok=True)
    
    zip_filename = f"rvu{year[-2:]}a.zip"
    cached_zip = cache_path / zip_filename
    
    # Check cache first
    if cached_zip.exists():
        print(f"Using cached file: {cached_zip}")
        return cached_zip
    
    # Download from CMS
    url = CMS_RVU_URLS.get(year)
    if not url:
        raise ValueError(f"No URL configured for year {year}")
    
    print(f"Downloading CMS RVU file for {year} from {url}...")
    
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=60) as response:
            data = response.read()
            
        with open(cached_zip, "wb") as f:
            f.write(data)
            
        print(f"Downloaded and cached: {cached_zip}")
        return cached_zip
        
    except (URLError, HTTPError) as e:
        raise RuntimeError(f"Failed to download CMS file: {e}")


def extract_rvu_excel_from_zip(zip_path: Path) -> bytes:
    """
    Extract the RVU Excel file from the CMS ZIP archive.
    
    The RVU file is typically named like 'PPRRVU25_JAN.xlsx' or similar.
    """
    with zipfile.ZipFile(zip_path, 'r') as zf:
        # Find the main RVU file
        rvu_files = [
            name for name in zf.namelist()
            if re.match(r'.*PPRRVU\d+.*\.xlsx?', name, re.IGNORECASE)
            or re.match(r'.*RVU\d+.*\.xlsx?', name, re.IGNORECASE)
        ]
        
        if not rvu_files:
            # Fall back to any Excel file
            rvu_files = [name for name in zf.namelist() if name.endswith(('.xlsx', '.xls'))]
        
        if not rvu_files:
            raise ValueError(f"No RVU Excel file found in {zip_path}")
        
        # Use the first matching file (usually there's only one main RVU file)
        rvu_file = rvu_files[0]
        print(f"Extracting: {rvu_file}")
        
        return zf.read(rvu_file), rvu_file


def find_column(df_columns: list, target_names: list) -> Optional[str]:
    """Find the actual column name matching one of the target names."""
    df_cols_upper = {c.upper().strip(): c for c in df_columns}
    for target in target_names:
        if target.upper() in df_cols_upper:
            return df_cols_upper[target.upper()]
    return None


def parse_rvu_data_pandas(excel_bytes: bytes) -> dict[str, RVURecord]:
    """Parse RVU data using pandas (preferred method)."""
    if not PANDAS_AVAILABLE:
        raise ImportError("pandas is required for Excel parsing")
    
    # Read Excel file
    df = pd.read_excel(BytesIO(excel_bytes), sheet_name=0)
    
    # Find columns
    columns = {}
    for key, possible_names in COLUMN_MAPPINGS.items():
        col = find_column(df.columns.tolist(), possible_names)
        if col:
            columns[key] = col
    
    if "hcpcs" not in columns:
        raise ValueError("Could not find HCPCS/CPT column in RVU file")
    
    records = {}
    
    for _, row in df.iterrows():
        hcpcs = str(row.get(columns.get("hcpcs"), "")).strip()
        if not hcpcs or hcpcs == "nan":
            continue
            
        # Normalize code (remove leading zeros, handle add-on notation)
        hcpcs = hcpcs.lstrip("0") if hcpcs.isdigit() else hcpcs
        
        def safe_float(val):
            try:
                if pd.isna(val) or val == "" or val is None:
                    return None
                return float(val)
            except (ValueError, TypeError):
                return None
        
        def safe_int(val):
            try:
                if pd.isna(val) or val == "" or val is None:
                    return 0
                return int(float(val))
            except (ValueError, TypeError):
                return 0
        
        record = RVURecord(
            hcpcs=hcpcs,
            modifier=str(row.get(columns.get("modifier"), "")).strip() if columns.get("modifier") else "",
            description=str(row.get(columns.get("description"), "")).strip() if columns.get("description") else "",
            work_rvu=safe_float(row.get(columns.get("work_rvu"))),
            nonfac_pe_rvu=safe_float(row.get(columns.get("nonfac_pe_rvu"))),
            fac_pe_rvu=safe_float(row.get(columns.get("fac_pe_rvu"))),
            mp_rvu=safe_float(row.get(columns.get("mp_rvu"))),
            nonfac_total_rvu=safe_float(row.get(columns.get("nonfac_total"))),
            fac_total_rvu=safe_float(row.get(columns.get("fac_total"))),
            global_days=str(row.get(columns.get("global_days"), "")).strip() if columns.get("global_days") else "",
            mult_proc_indicator=safe_int(row.get(columns.get("mult_proc"))),
            status_code=str(row.get(columns.get("status"), "")).strip() if columns.get("status") else "",
            pctc_indicator=safe_int(row.get(columns.get("pctc")))
        )
        
        # Use base code (no modifier) as primary, but keep modifier-specific if different
        key = hcpcs if not record.modifier else f"{hcpcs}-{record.modifier}"
        
        # Prefer records without modifiers for base values
        if hcpcs not in records or not record.modifier:
            if hcpcs in ALL_IP_CODES or key in ALL_IP_CODES:
                records[hcpcs] = record
    
    return records


# =============================================================================
# Integration Functions
# =============================================================================

def fetch_ip_rvu_data(year: str = "2025", cache_dir: str = "./cache") -> tuple[dict[str, RVURecord], str]:
    """
    Fetch CMS RVU data and extract IP-relevant codes.
    
    Returns:
        Tuple of (dict of RVURecords, source filename)
    """
    # Download/cache the CMS file
    zip_path = download_cms_rvu_file(year, cache_dir)
    
    # Extract Excel file
    excel_bytes, source_file = extract_rvu_excel_from_zip(zip_path)
    
    # Parse data
    all_records = parse_rvu_data_pandas(excel_bytes)
    
    # Filter to IP-relevant codes
    ip_records = {}
    for code in ALL_IP_CODES:
        # Try with and without leading zeros
        if code in all_records:
            ip_records[code] = all_records[code]
        elif code.zfill(5) in all_records:
            ip_records[code] = all_records[code.zfill(5)]
    
    return ip_records, source_file


def validate_against_existing(
    cms_data: dict[str, RVURecord],
    existing_json_path: str,
    tolerance: float = 0.05
) -> list[ValidationResult]:
    """
    Validate existing knowledge base against CMS source data.
    
    Args:
        cms_data: Dict of RVURecords from CMS
        existing_json_path: Path to existing IP coding JSON
        tolerance: Acceptable percentage difference (0.05 = 5%)
        
    Returns:
        List of ValidationResult objects
    """
    issues = []
    
    with open(existing_json_path, 'r') as f:
        existing = json.load(f)
    
    # Check fee_schedules section
    for schedule_name, schedule_data in existing.get("fee_schedules", {}).items():
        codes = schedule_data.get("codes", {})
        for code, code_data in codes.items():
            # Normalize code (remove + prefix for lookup)
            lookup_code = code.lstrip("+")
            
            if lookup_code not in cms_data:
                issues.append(ValidationResult(
                    code=code,
                    field="existence",
                    existing_value="present",
                    cms_value="not found",
                    severity="warning"
                ))
                continue
            
            cms_record = cms_data[lookup_code]
            
            # Check work RVU
            if "work_rvu" in code_data and cms_record.work_rvu is not None:
                existing_val = code_data["work_rvu"]
                cms_val = cms_record.work_rvu
                if existing_val and abs(existing_val - cms_val) > tolerance * cms_val:
                    issues.append(ValidationResult(
                        code=code,
                        field="work_rvu",
                        existing_value=existing_val,
                        cms_value=cms_val,
                        difference=round(existing_val - cms_val, 2),
                        severity="error" if abs(existing_val - cms_val) > 0.5 else "warning"
                    ))
            
            # Check facility total RVU
            if "total_facility_rvu" in code_data and cms_record.fac_total_rvu is not None:
                existing_val = code_data["total_facility_rvu"]
                cms_val = cms_record.fac_total_rvu
                if existing_val and abs(existing_val - cms_val) > tolerance * cms_val:
                    issues.append(ValidationResult(
                        code=code,
                        field="total_facility_rvu",
                        existing_value=existing_val,
                        cms_value=cms_val,
                        difference=round(existing_val - cms_val, 2),
                        severity="warning"
                    ))
            
            # Check non-facility total RVU
            if "total_nonfacility_rvu" in code_data and cms_record.nonfac_total_rvu is not None:
                existing_val = code_data["total_nonfacility_rvu"]
                cms_val = cms_record.nonfac_total_rvu
                if existing_val and abs(existing_val - cms_val) > tolerance * cms_val:
                    issues.append(ValidationResult(
                        code=code,
                        field="total_nonfacility_rvu",
                        existing_value=existing_val,
                        cms_value=cms_val,
                        difference=round(existing_val - cms_val, 2),
                        severity="warning"
                    ))
    
    return issues


def generate_rvu_section(cms_data: dict[str, RVURecord]) -> dict:
    """
    Generate the RVU sections for the knowledge base from CMS data.
    
    Returns a dict structured for the IP coding JSON.
    """
    # Organize by category
    categories = {
        "bronchoscopy": {},
        "pleural": {},
        "thoracoscopy": {},
        "sedation": {},
        "em": {},
        "imaging": {}
    }
    
    for code, record in cms_data.items():
        # Determine category
        category = None
        for cat_name, cat_codes in IP_CPT_CODES.items():
            if code in cat_codes or code.lstrip("0") in cat_codes:
                category = cat_name
                break
        
        if not category:
            continue
        
        # Format code key (add + prefix for add-on codes)
        code_key = f"+{code}" if record.is_add_on else code
        
        categories[category][code_key] = {
            "description": record.description,
            "work_rvu": record.work_rvu,
            "facility_pe_rvu": record.fac_pe_rvu,
            "nonfacility_pe_rvu": record.nonfac_pe_rvu,
            "mp_rvu": record.mp_rvu,
            "total_facility_rvu": record.fac_total_rvu,
            "total_nonfacility_rvu": record.nonfac_total_rvu,
            "global_days": record.global_days,
            "mult_proc_indicator": record.mult_proc_indicator,
            "status_code": record.status_code
        }
    
    return categories


def update_knowledge_base(
    existing_json_path: str,
    cms_data: dict[str, RVURecord],
    output_path: str,
    source_info: dict
) -> IntegrationReport:
    """
    Update the knowledge base with CMS RVU data.
    
    Args:
        existing_json_path: Path to existing IP coding JSON
        cms_data: Dict of RVURecords from CMS
        output_path: Path for updated JSON output
        source_info: Dict with source year and filename
        
    Returns:
        IntegrationReport with details of the update
    """
    report = IntegrationReport(
        cms_source_year=source_info.get("year", ""),
        cms_source_file=source_info.get("filename", ""),
        conversion_factor=32.7442  # 2025 CF
    )
    
    # Load existing data
    with open(existing_json_path, 'r') as f:
        data = json.load(f)
    
    # Update version
    old_version = data.get("version", "0.0")
    major, minor = old_version.split(".")[:2]
    data["version"] = f"{major}.{int(minor) + 1}"
    data["metadata"]["label"] = f"ip_coding_billing.v{data['version']}"
    data["metadata"]["updated_on"] = datetime.now().strftime("%Y-%m-%d")
    
    # Add CMS source info
    if "changelog" not in data["metadata"]:
        data["metadata"]["changelog"] = []
    data["metadata"]["changelog"].insert(0, 
        f"v{data['version']}: Updated RVU values from CMS {source_info.get('year')} PFS ({source_info.get('filename')})"
    )
    
    # Add CMS source reference
    data["metadata"]["cms_rvu_source"] = {
        "year": source_info.get("year"),
        "file": source_info.get("filename"),
        "conversion_factor": report.conversion_factor,
        "retrieved_on": datetime.now().strftime("%Y-%m-%d")
    }
    
    # Generate new authoritative RVU section
    rvu_categories = generate_rvu_section(cms_data)
    
    # Replace/add cms_rvus section with authoritative CMS data
    data["cms_rvus"] = {
        "_source": f"CMS {source_info.get('year')} Physician Fee Schedule",
        "_conversion_factor": report.conversion_factor,
        "_notes": [
            "These values are extracted directly from CMS PFS Relative Value Files.",
            "total_facility_rvu and total_nonfacility_rvu are the sum of work + PE + MP RVUs.",
            "Payments can be calculated by multiplying total RVUs by the conversion factor.",
            "Add-on codes (prefixed with +) have global_days='ZZZ' and status_code='A'."
        ],
        "bronchoscopy": rvu_categories.get("bronchoscopy", {}),
        "pleural": rvu_categories.get("pleural", {}),
        "thoracoscopy": rvu_categories.get("thoracoscopy", {}),
        "sedation": rvu_categories.get("sedation", {}),
        "em": rvu_categories.get("em", {}),
        "imaging": rvu_categories.get("imaging", {})
    }
    
    # Update fee_schedules with CMS-validated values
    for schedule_name, schedule_data in data.get("fee_schedules", {}).items():
        codes = schedule_data.get("codes", {})
        for code in list(codes.keys()):
            lookup_code = code.lstrip("+")
            if lookup_code in cms_data:
                cms_record = cms_data[lookup_code]
                # Update with CMS values
                if cms_record.work_rvu is not None:
                    codes[code]["work_rvu"] = cms_record.work_rvu
                if cms_record.fac_total_rvu is not None:
                    codes[code]["total_facility_rvu"] = cms_record.fac_total_rvu
                if cms_record.nonfac_total_rvu is not None:
                    codes[code]["total_nonfacility_rvu"] = cms_record.nonfac_total_rvu
                if cms_record.fac_payment is not None:
                    codes[code]["mpfs_facility_payment"] = int(round(cms_record.fac_payment))
                if cms_record.nonfac_payment is not None:
                    codes[code]["mpfs_nonfacility_payment"] = int(round(cms_record.nonfac_payment))
    
    # Validate and record issues
    report.validation_issues = validate_against_existing(cms_data, existing_json_path)
    report.ip_codes_extracted = len(cms_data)
    
    # Find missing codes
    for code in ALL_IP_CODES:
        if code not in cms_data:
            report.codes_not_found.append(code)
    
    # Write updated file
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    return report


# =============================================================================
# CLI Interface
# =============================================================================

def main():
    """Main entry point for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Fetch CMS RVU data and integrate with IP coding knowledge base"
    )
    parser.add_argument(
        "--year", "-y",
        default="2025",
        help="Fee schedule year (default: 2025)"
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to existing IP coding JSON file"
    )
    parser.add_argument(
        "--output", "-o",
        help="Path for updated JSON output (default: input with _cms_updated suffix)"
    )
    parser.add_argument(
        "--cache-dir",
        default="./cache",
        help="Directory for caching downloaded files"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate existing data against CMS, don't update"
    )
    parser.add_argument(
        "--report", "-r",
        help="Path for integration report JSON output"
    )
    
    args = parser.parse_args()
    
    # Set default output path
    if not args.output:
        base = Path(args.input).stem
        args.output = str(Path(args.input).parent / f"{base}_cms_updated.json")
    
    print(f"Fetching CMS RVU data for {args.year}...")
    cms_data, source_file = fetch_ip_rvu_data(args.year, args.cache_dir)
    print(f"Extracted {len(cms_data)} IP-relevant codes from {source_file}")
    
    if args.validate_only:
        print("\nValidating existing data against CMS source...")
        issues = validate_against_existing(cms_data, args.input)
        
        if issues:
            print(f"\nFound {len(issues)} validation issues:")
            for issue in issues:
                print(f"  [{issue.severity.upper()}] {issue.code}.{issue.field}: "
                      f"existing={issue.existing_value}, CMS={issue.cms_value}")
        else:
            print("\nNo validation issues found!")
        return
    
    print(f"\nUpdating knowledge base...")
    report = update_knowledge_base(
        args.input,
        cms_data,
        args.output,
        {"year": args.year, "filename": source_file}
    )
    
    print(f"\nIntegration complete!")
    print(f"  - Codes extracted: {report.ip_codes_extracted}")
    print(f"  - Codes not found: {len(report.codes_not_found)}")
    print(f"  - Validation issues: {len(report.validation_issues)}")
    print(f"  - Output: {args.output}")
    
    # Save report if requested
    if args.report:
        with open(args.report, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)
        print(f"  - Report: {args.report}")
    
    # Print any errors
    errors = [v for v in report.validation_issues if v.severity == "error"]
    if errors:
        print(f"\n⚠️  {len(errors)} ERROR-level issues found:")
        for e in errors[:10]:
            print(f"    {e.code}.{e.field}: existing={e.existing_value}, CMS={e.cms_value}")


if __name__ == "__main__":
    main()
