# CMS RVU Data Integration System for IP Coding Knowledge Base

## Overview

This system provides tools to link your Interventional Pulmonology (IP) coding knowledge base with authoritative CMS Physician Fee Schedule (PFS) Relative Value Unit (RVU) data. This ensures your coding assistance tool always uses accurate, up-to-date payment values.

## Why This Matters

Vendor reimbursement guides (Boston Scientific, Noah Medical, etc.) are helpful but:
- May use different rounding conventions
- Can become outdated mid-year
- Sometimes have transcription errors
- May not include all codes you need

By linking directly to CMS source data, you get:
- **Authoritative values** - Direct from CMS PFS files
- **Complete data** - All RVU components (Work, PE, MP)
- **Audit trail** - Know exactly where values came from
- **Easy updates** - Refresh annually or quarterly

## System Components

```
cms_rvu_integration/
├── rvu_fetcher.py          # Network-based CMS file fetcher (requires internet)
├── local_rvu_updater.py    # Local CSV-based updater (no network required)
├── cms_rvus_2025_ip.csv    # Pre-populated 2025 RVU data for IP codes
└── README.md               # This documentation
```

## Quick Start

### Option 1: Use Pre-Populated CSV (Recommended)

The examples below assume `data/knowledge/ip_coding_billing.v2_7.json` as the current baseline. The updater will increment the minor version automatically.

```bash
# Update your JSON with the included 2025 RVU data
python local_rvu_updater.py update \
    --input data/knowledge/ip_coding_billing.v2_7.json \
    --rvu-csv cms_rvus_2025_ip.csv \
    --output data/knowledge/ip_coding_billing.v2_7.json \
    --source "CMS 2025 PFS Final Rule"
```

### Option 2: Download Fresh CMS Data

```bash
# Requires internet and pandas/openpyxl
pip install pandas openpyxl

python rvu_fetcher.py \
    --year 2025 \
    --input data/knowledge/ip_coding_billing.v2_7.json \
    --output data/knowledge/ip_coding_billing.v2_7.json \
    --report integration_report.json
```

### Option 3: Generate Template and Fill Manually

```bash
# Generate blank template with all IP codes
python local_rvu_updater.py template --output my_rvus.csv

# Fill in data from CMS website, then update
python local_rvu_updater.py update \
    --input data/knowledge/ip_coding_billing.v2_7.json \
    --rvu-csv my_rvus.csv \
    --output data/knowledge/ip_coding_billing.v2_7.json
```

## CSV Format

The CSV should have these columns (names are flexible):

| Column | Description | Example |
|--------|-------------|---------|
| HCPCS | CPT/HCPCS code | 31628 |
| DESCRIPTION | Code description | Bronch w/lung bx 1 lobe |
| WORK_RVU | Work RVU | 3.55 |
| NON_FAC_PE_RVU | Non-facility Practice Expense RVU | 7.56 |
| FAC_PE_RVU | Facility Practice Expense RVU | 1.60 |
| MP_RVU | Malpractice RVU | 0.38 |
| NON_FAC_TOTAL | Total non-facility RVU | 11.49 |
| FAC_TOTAL | Total facility RVU | 5.53 |
| GLOB_DAYS | Global period (000, 010, 090, XXX, ZZZ) | 000 |
| MULT_PROC | Multiple Procedure indicator | 3 |
| STATUS | Status code (A=active) | A |

## Where to Get CMS Data

### Official CMS Downloads

1. Go to: https://www.cms.gov/medicare/payment/fee-schedules/physician/pfs-relative-value-files
2. Download the current year's RVU file (e.g., "RVU25A.zip")
3. Extract and open the Excel file (e.g., "PPRRVU25_JAN.xlsx")
4. Filter to the codes you need or export all to CSV

### CMS Fee Schedule Lookup Tool

For individual codes:
https://www.cms.gov/medicare/payment/fee-schedules/physician/search

### MAC-Specific Locality Adjustments

For locality-adjusted (GPCI) values:
https://www.cms.gov/medicare/payment/fee-schedules/physician/pfs-federal-regulation-notices

## Understanding the Output

After running the updater, your JSON will have a new `cms_rvus` section. As of December 2025, these examples assume `data/knowledge/ip_coding_billing.v2_7.json` with a `cms_rvus` block structured like the following:

```json
{
  "cms_rvus": {
    "_source": "CMS 2025 PFS Final Rule",
    "_conversion_factor": 32.3562,
    "_updated_on": "2025-01-15",
    "_notes": [...],
    
    "bronchoscopy": {
      "31628": {
        "description": "Bronch w/lung bx 1 lobe",
        "work_rvu": 3.55,
        "facility_pe_rvu": 1.60,
        "nonfacility_pe_rvu": 7.56,
        "mp_rvu": 0.38,
        "total_facility_rvu": 5.53,
        "total_nonfacility_rvu": 11.49,
        "mpfs_facility_payment": 181,
        "mpfs_nonfacility_payment": 376,
        "global_days": "000",
        "mult_proc_indicator": 3,
        "status_code": "A",
        "is_add_on": false
      },
      "+31632": {
        "description": "Bronch tblb addl lobe",
        ...
        "is_add_on": true
      }
    },
    
    "pleural": {...},
    "thoracoscopy": {...},
    "sedation": {...},
    "em": {...}
  }
}
```

## Key Data Elements Explained

### RVU Components

- **Work RVU**: Reflects physician work (time, skill, intensity)
- **Practice Expense (PE) RVU**: 
  - *Facility*: When performed in hospital/ASC (lower PE)
  - *Non-Facility*: When performed in office (higher PE, includes equipment)
- **Malpractice (MP) RVU**: Professional liability insurance cost

### Payment Calculation

```
Payment = Total RVU × Conversion Factor × GPCI adjustments

Where:
- Total RVU = Work RVU + PE RVU + MP RVU
- 2025 Conversion Factor = $32.3562
- GPCI = Geographic Practice Cost Index (varies by locality)
```

### Global Period Codes

| Code | Meaning |
|------|---------|
| 000 | Endoscopic/minor procedure (no post-op period) |
| 010 | 10-day global (minor surgery) |
| 090 | 90-day global (major surgery) |
| XXX | Global period doesn't apply |
| ZZZ | Add-on code (reports with primary) |

### Multiple Procedure Indicator

| Value | Meaning |
|-------|---------|
| 0 | No reduction rules apply |
| 2 | 100% for highest, 50% for second, 25% for third+ |
| 3 | Endoscopy base procedure rules (multiple endoscopy) |

### Status Codes

| Code | Meaning |
|-------|---------|
| A | Active code, separately payable |
| B | Bundled (payment included in other service) |
| C | Carrier-priced |
| I | Invalid for Medicare |
| N | Non-covered |

## Validation Features

### Validate Without Updating

```bash
python local_rvu_updater.py validate \
    --input data/knowledge/ip_coding_billing.v2_7.json \
    --rvu-csv cms_rvus_2025_ip.csv
```

This compares your existing JSON against the CSV and reports:
- Codes with different Work RVU values
- Codes in JSON but not in CSV
- Codes with significant payment differences

### Tolerance Settings

The validation uses a 5% tolerance by default. Values within 5% of CMS source are considered acceptable (accounts for rounding differences in vendor guides).

## Annual Update Workflow

1. **January**: CMS releases final PFS for the year
2. **Download** new RVU file from CMS
3. **Run** the updater to refresh your knowledge base
4. **Review** the integration report for any issues
5. **Test** your coding assistant with updated values

## Troubleshooting

### "Could not find HCPCS column"
- Check CSV column headers match expected format
- Ensure file encoding is UTF-8
- Try renaming column to "HCPCS" or "CPT"

### Missing codes in output
- Code may not be in the IP_CPT_CODES list
- Add codes to the list in the Python script
- Or include all codes by modifying the filter

### Payment values seem wrong
- Check conversion factor setting
- Verify you're using facility vs non-facility appropriately
- Remember payments shown are national unadjusted (no GPCI)

## Integration with IP_assist_lite

To use this data in your chatbot:

```python
import json

# Load the updated knowledge base
with open('data/knowledge/ip_coding_billing.v2_7.json') as f:
    coding_data = json.load(f)

# Access CMS-validated RVU data
bronch_codes = coding_data['cms_rvus']['bronchoscopy']

# Look up a specific code
code_31628 = bronch_codes['31628']
print(f"31628 Facility Payment: ${code_31628['mpfs_facility_payment']}")
```

## References

- [CMS PFS Overview](https://www.cms.gov/medicare/payment/fee-schedules/physician)
- [RVU File Downloads](https://www.cms.gov/medicare/payment/fee-schedules/physician/pfs-relative-value-files)
- [NCCI Manual](https://www.cms.gov/medicare/coding-billing/national-correct-coding-initiative-ncci)
- [AABIP Coding Resources](https://aabip.org/resources/)

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.1 | 2025-12-01 | Added --family filter, --strict mode for CI, tokenized text matching in terminology_utils, corrected E/M RVU values |
| 1.0 | 2025-06-01 | Initial release with 2025 PFS data |

---

*This system is for reference and educational purposes. Always verify coding decisions with current CMS publications and qualified coding professionals.*
