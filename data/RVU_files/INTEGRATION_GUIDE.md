# RVU Calculator Integration Guide for Procedure_suite

## Overview
This guide explains how to integrate the CMS RVU parser into your Procedure_suite v3 branch to add RVU calculations to the CPT coder module.

## Files Created

### Core Parser Module
- **cms_rvu_parser.py**: Main parser with RVU calculation logic
- **sample_rvu_2025.csv**: Sample 2025 RVU data (52 procedures)
- **gpci_2025.csv**: Geographic Practice Cost Indices for 81 US localities
- **demo.py**: Comprehensive demonstration of all features
- **bronchoscopy_codes_2025.csv**: Exported bronchoscopy-specific codes

## Key Features

### 1. RVU Data Management
- Parse CMS RVU files (fixed-width or CSV format)
- Store and query CPT/HCPCS codes with RVU values
- Handle modifiers (-26, -TC, -50, -51, etc.)
- Export to pandas DataFrame for analysis

### 2. Payment Calculations
```python
payment = parser.calculate_payment(
    hcpcs_code='31653',
    setting='facility',  # or 'non-facility'
    work_gpci=Decimal('1.022'),
    pe_gpci=Decimal('1.120'),
    mp_gpci=Decimal('0.700')
)
# Returns: payment amount, adjusted RVUs, and breakdown
```

### 3. Geographic Adjustments
- GPCI data for all US Medicare localities
- Automatic adjustment of Work, PE, and MP RVUs
- Payment calculations specific to practice location

### 4. Provider Productivity
- Track Work RVUs for physician productivity
- Calculate revenue projections
- Analyze procedure complexity distribution

## Integration Steps for Procedure_suite

### Step 1: Copy Parser Module

```bash
# From the rvu_parser directory
cp cms_rvu_parser.py /path/to/Procedure_suite/proc_autocode/rvu/
cp sample_rvu_2025.csv /path/to/Procedure_suite/proc_autocode/rvu/data/
cp gpci_2025.csv /path/to/Procedure_suite/proc_autocode/rvu/data/
```

### Step 2: Update proc_autocode Structure

Add to your existing proc_autocode module:

```
proc_autocode/
├── __init__.py
├── coder.py              # Your existing coder
├── rvu/
│   ├── __init__.py
│   ├── rvu_parser.py     # Renamed from cms_rvu_parser.py
│   ├── rvu_calculator.py # New calculator class
│   ├── data/
│   │   ├── rvu_2025.csv
│   │   └── gpci_2025.csv
│   └── updater.py        # CMS data auto-updater
```

### Step 3: Create RVU Calculator Wrapper

**File: `proc_autocode/rvu/rvu_calculator.py`**

```python
"""
RVU Calculator for Procedure Suite
Wraps CMS parser with project-specific functionality
"""

from pathlib import Path
from typing import Dict, List, Optional
from decimal import Decimal

from .rvu_parser import CMSRVUParser, GPCIRecord
import pandas as pd


class ProcedureRVUCalculator:
    """RVU calculator integrated with Procedure Suite"""
    
    def __init__(self, rvu_file: Path, gpci_file: Path):
        self.parser = CMSRVUParser()
        self.parser.parse_csv_file(rvu_file)
        self.gpci_data = self._load_gpci(gpci_file)
        
    def _load_gpci(self, file_path: Path) -> Dict[str, GPCIRecord]:
        """Load GPCI data"""
        gpci_dict = {}
        df = pd.read_csv(file_path, dtype={'locality_code': str})
        
        for _, row in df.iterrows():
            code = str(row['locality_code']).strip()
            if len(code) <= 2:
                code = code.zfill(2)
            gpci_dict[code] = GPCIRecord(
                locality_code=code,
                locality_name=row['locality_name'],
                work_gpci=Decimal(str(row['work_gpci'])),
                pe_gpci=Decimal(str(row['pe_gpci'])),
                mp_gpci=Decimal(str(row['mp_gpci']))
            )
        return gpci_dict
    
    def calculate_procedure_rvu(
        self,
        cpt_code: str,
        locality: str = '00',  # National average
        setting: str = 'facility',
        modifiers: List[str] = None
    ) -> Optional[Dict]:
        """
        Calculate RVU and payment for a procedure
        
        Returns dict with:
        - work_rvu, pe_rvu, mp_rvu, total_rvu
        - payment_amount
        - geographic adjustments
        """
        gpci = self.gpci_data.get(locality)
        if not gpci:
            gpci = self.gpci_data['00']  # Fall back to national
        
        result = self.parser.calculate_payment(
            hcpcs_code=cpt_code,
            setting=setting,
            work_gpci=gpci.work_gpci,
            pe_gpci=gpci.pe_gpci,
            mp_gpci=gpci.mp_gpci
        )
        
        # Apply modifier adjustments if needed
        if result and modifiers:
            result = self._apply_modifiers(result, modifiers)
        
        return result
    
    def _apply_modifiers(self, base_result: Dict, modifiers: List[str]) -> Dict:
        """Apply modifier-based adjustments"""
        result = base_result.copy()
        
        for mod in modifiers:
            if mod == '50':  # Bilateral
                result['payment_amount'] *= 1.5
                result['total_adjusted_rvu'] *= 1.5
            elif mod == '51':  # Multiple procedures
                result['payment_amount'] *= 0.5
                result['total_adjusted_rvu'] *= 0.5
            elif mod == '52':  # Reduced services
                result['payment_amount'] *= 0.5
                result['total_adjusted_rvu'] *= 0.5
            elif mod == '62':  # Two surgeons
                result['payment_amount'] *= 0.625  # Each gets 62.5%
        
        return result
    
    def calculate_case_rvu(
        self,
        procedures: List[Dict],
        locality: str = '00',
        setting: str = 'facility'
    ) -> Dict:
        """
        Calculate total RVU for multiple procedures
        
        Args:
            procedures: List of dicts with 'cpt_code', 'modifiers', 'multiplier'
            
        Returns:
            Total work RVUs, payment, and breakdown by procedure
        """
        total_wrvu = Decimal('0')
        total_payment = 0.0
        breakdown = []
        
        for i, proc in enumerate(procedures):
            result = self.calculate_procedure_rvu(
                cpt_code=proc['cpt_code'],
                locality=locality,
                setting=setting,
                modifiers=proc.get('modifiers', [])
            )
            
            if result:
                # Apply multiple procedure discount
                multiplier = proc.get('multiplier', 1.0 if i == 0 else 0.5)
                
                proc_payment = result['payment_amount'] * multiplier
                proc_wrvu = Decimal(str(result['work_rvu'])) * Decimal(str(multiplier))
                
                total_wrvu += proc_wrvu
                total_payment += proc_payment
                
                breakdown.append({
                    'cpt_code': proc['cpt_code'],
                    'work_rvu': float(proc_wrvu),
                    'payment': proc_payment,
                    'multiplier': multiplier
                })
        
        return {
            'total_work_rvu': float(total_wrvu),
            'total_payment': total_payment,
            'procedure_count': len(procedures),
            'breakdown': breakdown
        }
```

### Step 4: Integrate with Existing Coder

**Update: `proc_autocode/coder.py`**

```python
from .rvu.rvu_calculator import ProcedureRVUCalculator
from pathlib import Path

class EnhancedCPTCoder:
    def __init__(self, config):
        # Existing initialization
        self.config = config
        
        # NEW: Initialize RVU calculator
        rvu_dir = Path(__file__).parent / 'rvu' / 'data'
        self.rvu_calc = ProcedureRVUCalculator(
            rvu_file=rvu_dir / 'rvu_2025.csv',
            gpci_file=rvu_dir / 'gpci_2025.csv'
        )
    
    def code_procedure(self, procedure_data):
        """Code a procedure and calculate RVUs"""
        
        # Existing coding logic
        codes = self._generate_codes(procedure_data)
        
        # NEW: Add RVU calculations
        locality = procedure_data.get('locality', '00')
        setting = procedure_data.get('setting', 'facility')
        
        procedures = []
        for i, code in enumerate(codes):
            procedures.append({
                'cpt_code': code.cpt,
                'modifiers': code.modifiers,
                'multiplier': 1.0 if i == 0 else 0.5  # Multiple procedure rule
            })
        
        # Calculate case-level RVUs
        rvu_results = self.rvu_calc.calculate_case_rvu(
            procedures=procedures,
            locality=locality,
            setting=setting
        )
        
        # Attach RVU data to codes
        for code, proc_rvu in zip(codes, rvu_results['breakdown']):
            code.rvu_data = proc_rvu
        
        # Add summary
        case_summary = {
            'codes': codes,
            'total_work_rvu': rvu_results['total_work_rvu'],
            'estimated_payment': rvu_results['total_payment'],
            'locality': locality
        }
        
        return case_summary
```

### Step 5: Update API Endpoints

**File: `api/rvu_routes.py`**

```python
from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/rvu", tags=["RVU Calculations"])


class RVURequest(BaseModel):
    cpt_code: str
    locality: str = "00"
    setting: str = "facility"
    modifiers: Optional[List[str]] = None


class CaseRVURequest(BaseModel):
    procedures: List[dict]
    locality: str = "00"
    setting: str = "facility"


@router.post("/calculate")
async def calculate_single_rvu(request: RVURequest):
    """Calculate RVU for a single procedure"""
    # Implementation using rvu_calc
    pass


@router.post("/calculate/case")
async def calculate_case_rvu(request: CaseRVURequest):
    """Calculate total RVUs for a case with multiple procedures"""
    pass


@router.get("/localities")
async def get_localities():
    """List available geographic localities"""
    pass


@router.get("/code/{cpt_code}")
async def get_code_details(cpt_code: str):
    """Get detailed RVU breakdown for a code"""
    pass
```

### Step 6: Database Schema Updates

**Add to your Supabase schema:**

```sql
-- RVU master data table
CREATE TABLE rvu_data (
    cpt_code VARCHAR(5) PRIMARY KEY,
    work_rvu DECIMAL(10,2),
    pe_rvu_nonfac DECIMAL(10,2),
    pe_rvu_fac DECIMAL(10,2),
    mp_rvu DECIMAL(10,2),
    conversion_factor DECIMAL(10,4),
    effective_date DATE,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- GPCI data
CREATE TABLE gpci_data (
    locality_code VARCHAR(5),
    locality_name VARCHAR(100),
    work_gpci DECIMAL(5,3),
    pe_gpci DECIMAL(5,3),
    mp_gpci DECIMAL(5,3),
    year INTEGER,
    PRIMARY KEY (locality_code, year)
);

-- Procedure RVU calculations (audit trail)
CREATE TABLE procedure_rvu_calculations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    procedure_id UUID REFERENCES procedures(id),
    cpt_code VARCHAR(5),
    work_rvu DECIMAL(10,2),
    total_rvu DECIMAL(10,2),
    payment_amount DECIMAL(10,2),
    locality_code VARCHAR(5),
    setting VARCHAR(20),
    calculated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_procedure_rvu_proc_id ON procedure_rvu_calculations(procedure_id);
CREATE INDEX idx_procedure_rvu_cpt ON procedure_rvu_calculations(cpt_code);
```

## Testing

Create test file: `tests/test_rvu_calculator.py`

```python
import pytest
from proc_autocode.rvu.rvu_calculator import ProcedureRVUCalculator
from pathlib import Path


@pytest.fixture
def calculator():
    rvu_file = Path('proc_autocode/rvu/data/rvu_2025.csv')
    gpci_file = Path('proc_autocode/rvu/data/gpci_2025.csv')
    return ProcedureRVUCalculator(rvu_file, gpci_file)


def test_basic_rvu_calculation(calculator):
    """Test basic RVU calculation"""
    result = calculator.calculate_procedure_rvu(
        cpt_code='31622',
        locality='00',
        setting='facility'
    )
    
    assert result is not None
    assert result['work_rvu'] == 3.50
    assert result['payment_amount'] > 0


def test_geographic_adjustment(calculator):
    """Test GPCI adjustments"""
    result_sd = calculator.calculate_procedure_rvu(
        cpt_code='31653',
        locality='05102',  # San Diego
        setting='facility'
    )
    
    result_national = calculator.calculate_procedure_rvu(
        cpt_code='31653',
        locality='00',  # National
        setting='facility'
    )
    
    # San Diego should have higher payment than national avg
    assert result_sd['payment_amount'] > result_national['payment_amount']


def test_multiple_procedures(calculator):
    """Test multiple procedure calculation"""
    procedures = [
        {'cpt_code': '31653', 'multiplier': 1.0},
        {'cpt_code': '31654', 'multiplier': 0.5},  # Add-on code
    ]
    
    result = calculator.calculate_case_rvu(
        procedures=procedures,
        locality='05102',
        setting='facility'
    )
    
    assert result['procedure_count'] == 2
    assert result['total_work_rvu'] > 0
    assert len(result['breakdown']) == 2


def test_modifier_application(calculator):
    """Test modifier adjustments"""
    base_result = calculator.calculate_procedure_rvu(
        cpt_code='31622',
        locality='00',
        setting='facility'
    )
    
    bilateral_result = calculator.calculate_procedure_rvu(
        cpt_code='31622',
        locality='00',
        setting='facility',
        modifiers=['50']  # Bilateral
    )
    
    # Bilateral should be 150% of base
    assert bilateral_result['payment_amount'] == pytest.approx(
        base_result['payment_amount'] * 1.5
    )
```

## Usage Examples

### Example 1: Code a bronchoscopy case

```python
from proc_autocode import EnhancedCPTCoder

coder = EnhancedCPTCoder(config)

procedure_data = {
    'procedure_type': 'bronchoscopy',
    'findings': 'EBUS-guided TBNA of station 4R and 7 lymph nodes',
    'locality': '05102',  # San Diego
    'setting': 'facility'
}

result = coder.code_procedure(procedure_data)

print(f"Codes: {[c.cpt for c in result['codes']]}")
print(f"Total Work RVUs: {result['total_work_rvu']:.2f}")
print(f"Estimated Payment: ${result['estimated_payment']:.2f}")
```

### Example 2: Provider productivity tracking

```python
# Track monthly productivity
monthly_procedures = [
    {'cpt': '31622', 'count': 10},
    {'cpt': '31625', 'count': 15},
    {'cpt': '31653', 'count': 12},
]

total_wrvu = 0
for proc in monthly_procedures:
    result = calculator.calculate_procedure_rvu(proc['cpt'])
    proc_wrvu = result['work_rvu'] * proc['count']
    total_wrvu += proc_wrvu
    
print(f"Monthly wRVUs: {total_wrvu:.2f}")
print(f"Annualized: {total_wrvu * 12:.2f}")
```

### Example 3: Revenue projection

```python
# Project revenue for procedure mix
case_mix = {
    '31622': 10,  # Diagnostic bronch
    '31625': 15,  # Bronch with biopsy
    '31653': 12,  # EBUS with TBNA
}

total_revenue = 0
for cpt, volume in case_mix.items():
    result = calculator.calculate_procedure_rvu(
        cpt, 
        locality='05102',
        setting='facility'
    )
    total_revenue += result['payment_amount'] * volume

print(f"Monthly Revenue: ${total_revenue:,.2f}")
print(f"Annual Projection: ${total_revenue * 12:,.2f}")
```

## Maintenance

### Quarterly RVU Updates

CMS releases updated RVU files quarterly. Create an updater:

**File: `proc_autocode/rvu/updater.py`**

```python
import requests
from pathlib import Path


def update_rvu_data(year: int, quarter: str):
    """
    Download latest RVU data from CMS
    
    Args:
        year: Year (e.g., 2025)
        quarter: A, B, C, or D
    """
    url = f"https://www.cms.gov/Medicare/Medicare-Fee-for-Service-Payment/PhysicianFeeSched/Downloads/RVU{str(year)[-2:]}{quarter}.zip"
    
    # Download and extract
    # Parse and update database
    pass
```

## Next Steps

1. **Immediate**:
   - Copy parser files to Procedure_suite
   - Run tests with sample data
   - Integrate with one procedure type (bronchoscopy)

2. **Short-term** (1-2 weeks):
   - Complete API endpoints
   - Add database persistence
   - Build dashboard visualizations

3. **Medium-term** (1 month):
   - Automated CMS data updates
   - Provider productivity dashboard
   - Revenue analytics

4. **Long-term** (3 months):
   - Machine learning for coding optimization
   - Payer-specific adjustments
   - Historical trend analysis

## Resources

- [CMS Physician Fee Schedule](https://www.cms.gov/medicare/physician-fee-schedule)
- [RVU File Downloads](https://www.cms.gov/medicare/payment/fee-schedules/physician/pfs-relative-value-files)
- [RBRVS Overview](https://www.ama-assn.org/about/rvs-update-committee-ruc/rbrvs-overview)

## Support

For questions or issues with RVU integration:
- Check demo.py for usage examples
- Review test cases for edge cases
- Consult CMS documentation for policy updates
