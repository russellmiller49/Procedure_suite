"""
CMS RVU File Parser
Parse Medicare Physician Fee Schedule Relative Value Unit files from CMS
"""

from dataclasses import dataclass
from typing import Optional, Dict, List
from decimal import Decimal
import requests
import io
import zipfile
import pandas as pd
from pathlib import Path


@dataclass
class RVURecord:
    """Represents a single RVU record from CMS file"""
    hcpcs_code: str
    modifier: str
    description: str
    status_code: str
    work_rvu: Optional[Decimal]
    non_fac_pe_rvu: Optional[Decimal]
    fac_pe_rvu: Optional[Decimal]
    mp_rvu: Optional[Decimal]
    total_non_fac_rvu: Optional[Decimal]
    total_fac_rvu: Optional[Decimal]
    pctc_indicator: str
    global_surgery: str
    mult_proc_indicator: str
    bilateral_surgery: str
    assistant_surgery: str
    co_surgeons: str
    team_surgery: str
    conversion_factor: Optional[Decimal]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'hcpcs_code': self.hcpcs_code,
            'modifier': self.modifier,
            'description': self.description,
            'status_code': self.status_code,
            'work_rvu': float(self.work_rvu) if self.work_rvu else None,
            'non_fac_pe_rvu': float(self.non_fac_pe_rvu) if self.non_fac_pe_rvu else None,
            'fac_pe_rvu': float(self.fac_pe_rvu) if self.fac_pe_rvu else None,
            'mp_rvu': float(self.mp_rvu) if self.mp_rvu else None,
            'total_non_fac_rvu': float(self.total_non_fac_rvu) if self.total_non_fac_rvu else None,
            'total_fac_rvu': float(self.total_fac_rvu) if self.total_fac_rvu else None,
            'pctc_indicator': self.pctc_indicator,
            'global_surgery': self.global_surgery,
            'mult_proc_indicator': self.mult_proc_indicator,
            'bilateral_surgery': self.bilateral_surgery,
            'conversion_factor': float(self.conversion_factor) if self.conversion_factor else None
        }


@dataclass
class GPCIRecord:
    """Geographic Practice Cost Index record"""
    locality_code: str
    locality_name: str
    work_gpci: Decimal
    pe_gpci: Decimal
    mp_gpci: Decimal


class CMSRVUParser:
    """Parser for CMS RVU files"""
    
    # File format specifications based on CMS documentation
    FIELD_SPECS = [
        ('hcpcs_code', 0, 5),
        ('modifier', 5, 7),
        ('description', 7, 57),
        ('status_code', 57, 58),
        ('work_rvu', 59, 65),
        ('trans_nonfac_pe_rvu', 66, 72),
        ('trans_nonfac_na', 72, 74),
        ('full_nonfac_pe_rvu', 75, 81),
        ('full_nonfac_na', 81, 83),
        ('trans_fac_pe_rvu', 84, 90),
        ('trans_fac_na', 90, 92),
        ('full_fac_pe_rvu', 93, 99),
        ('full_fac_na', 99, 101),
        ('mp_rvu', 103, 108),
        ('total_trans_nonfac_rvu', 109, 115),
        ('total_full_nonfac_rvu', 116, 122),
        ('total_trans_fac_rvu', 123, 129),
        ('total_full_fac_rvu', 130, 136),
        ('pctc_indicator', 138, 139),
        ('global_surgery', 139, 142),
        ('mult_proc', 151, 152),
        ('bilateral_surgery', 152, 153),
        ('assistant_surgery', 153, 154),
        ('co_surgeons', 154, 155),
        ('team_surgery', 155, 156),
        ('conversion_factor', 168, 176),
    ]
    
    def __init__(self):
        self.records: Dict[str, RVURecord] = {}
        self.gpci_records: Dict[str, GPCIRecord] = {}
        
    @staticmethod
    def parse_decimal(value: str) -> Optional[Decimal]:
        """Parse decimal value, handling NA and empty strings"""
        value = value.strip()
        if not value or value == 'NA':
            return None
        try:
            return Decimal(value)
        except:
            return None
    
    def parse_fixed_width_line(self, line: str) -> Optional[RVURecord]:
        """Parse a fixed-width format line into RVURecord"""
        if len(line) < 200:
            return None
            
        # Skip header lines
        if line.startswith('HDR'):
            return None
            
        try:
            hcpcs = line[0:5].strip()
            modifier = line[5:7].strip()
            description = line[7:57].strip()
            status_code = line[57:58].strip()
            
            # Parse RVU values - use transitioned values (current standard)
            work_rvu = self.parse_decimal(line[59:65])
            nonfac_pe = self.parse_decimal(line[66:72])
            fac_pe = self.parse_decimal(line[84:90])
            mp_rvu = self.parse_decimal(line[103:108])
            
            # Total RVUs
            total_nonfac = self.parse_decimal(line[109:115])
            total_fac = self.parse_decimal(line[123:129])
            
            # Indicators
            pctc = line[138:139].strip()
            global_surg = line[139:142].strip()
            mult_proc = line[151:152].strip()
            bilateral = line[152:153].strip()
            assistant = line[153:154].strip()
            co_surg = line[154:155].strip()
            team = line[155:156].strip()
            
            cf = self.parse_decimal(line[168:176])
            
            return RVURecord(
                hcpcs_code=hcpcs,
                modifier=modifier,
                description=description,
                status_code=status_code,
                work_rvu=work_rvu,
                non_fac_pe_rvu=nonfac_pe,
                fac_pe_rvu=fac_pe,
                mp_rvu=mp_rvu,
                total_non_fac_rvu=total_nonfac,
                total_fac_rvu=total_fac,
                pctc_indicator=pctc,
                global_surgery=global_surg,
                mult_proc_indicator=mult_proc,
                bilateral_surgery=bilateral,
                assistant_surgery=assistant,
                co_surgeons=co_surg,
                team_surgery=team,
                conversion_factor=cf
            )
        except Exception as e:
            print(f"Error parsing line: {e}")
            return None
    
    def parse_file(self, file_path: Path) -> int:
        """Parse RVU file and load records"""
        count = 0
        with open(file_path, 'r', encoding='latin-1', errors='ignore') as f:
            for line in f:
                record = self.parse_fixed_width_line(line)
                if record and record.hcpcs_code:
                    key = f"{record.hcpcs_code}_{record.modifier}" if record.modifier else record.hcpcs_code
                    self.records[key] = record
                    count += 1
        return count
    
    def parse_csv_file(self, file_path: Path) -> int:
        """Parse CSV format RVU file"""
        try:
            df = pd.read_csv(file_path, dtype=str)
            count = 0
            
            # Normalize column names
            df.columns = df.columns.str.strip()
            
            for _, row in df.iterrows():
                try:
                    record = RVURecord(
                        hcpcs_code=str(row['HCPCS']).strip() if pd.notna(row.get('HCPCS')) else '',
                        modifier=str(row['MOD']).strip() if pd.notna(row.get('MOD')) else '',
                        description=str(row['DESCRIPTION']).strip() if pd.notna(row.get('DESCRIPTION')) else '',
                        status_code=str(row['STATUS CODE']).strip() if pd.notna(row.get('STATUS CODE')) else '',
                        work_rvu=self.parse_decimal(str(row['WORK RVU'])) if pd.notna(row.get('WORK RVU')) else None,
                        non_fac_pe_rvu=self.parse_decimal(str(row['NON-FAC PE RVU'])) if pd.notna(row.get('NON-FAC PE RVU')) else None,
                        fac_pe_rvu=self.parse_decimal(str(row['FACILITY PE RVU'])) if pd.notna(row.get('FACILITY PE RVU')) else None,
                        mp_rvu=self.parse_decimal(str(row['MP RVU'])) if pd.notna(row.get('MP RVU')) else None,
                        total_non_fac_rvu=self.parse_decimal(str(row['NON-FAC TOTAL'])) if pd.notna(row.get('NON-FAC TOTAL')) else None,
                        total_fac_rvu=self.parse_decimal(str(row['FACILITY TOTAL'])) if pd.notna(row.get('FACILITY TOTAL')) else None,
                        pctc_indicator=str(row['PCTC IND']).strip() if pd.notna(row.get('PCTC IND')) else '',
                        global_surgery=str(row['GLOB DAYS']).strip() if pd.notna(row.get('GLOB DAYS')) else '',
                        mult_proc_indicator=str(row['MULT PROC']).strip() if pd.notna(row.get('MULT PROC')) else '',
                        bilateral_surgery=str(row['BILAT SURG']).strip() if pd.notna(row.get('BILAT SURG')) else '',
                        assistant_surgery=str(row['ASST SURG']).strip() if pd.notna(row.get('ASST SURG')) else '',
                        co_surgeons=str(row['CO-SURG']).strip() if pd.notna(row.get('CO-SURG')) else '',
                        team_surgery=str(row['TEAM SURG']).strip() if pd.notna(row.get('TEAM SURG')) else '',
                        conversion_factor=self.parse_decimal(str(row['CONV FACTOR'])) if pd.notna(row.get('CONV FACTOR')) else None
                    )
                    
                    if record.hcpcs_code:
                        key = f"{record.hcpcs_code}_{record.modifier}" if record.modifier else record.hcpcs_code
                        self.records[key] = record
                        count += 1
                except Exception as e:
                    continue
                    
            return count
        except Exception as e:
            print(f"Error parsing CSV: {e}")
            return 0
    
    def get_record(self, hcpcs_code: str, modifier: str = '') -> Optional[RVURecord]:
        """Get RVU record for a CPT/HCPCS code"""
        key = f"{hcpcs_code}_{modifier}" if modifier else hcpcs_code
        return self.records.get(key)
    
    def search_by_description(self, search_term: str) -> List[RVURecord]:
        """Search records by description"""
        results = []
        search_term = search_term.lower()
        for record in self.records.values():
            if search_term in record.description.lower():
                results.append(record)
        return results
    
    def get_active_codes(self) -> List[RVURecord]:
        """Get all active (status A) codes"""
        return [r for r in self.records.values() if r.status_code == 'A']
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert records to pandas DataFrame"""
        data = [r.to_dict() for r in self.records.values()]
        return pd.DataFrame(data)
    
    def calculate_payment(
        self, 
        hcpcs_code: str,
        setting: str = 'non-facility',
        work_gpci: Decimal = Decimal('1.0'),
        pe_gpci: Decimal = Decimal('1.0'),
        mp_gpci: Decimal = Decimal('1.0'),
        modifier: str = ''
    ) -> Optional[Dict]:
        """
        Calculate Medicare payment for a code
        
        Args:
            hcpcs_code: CPT or HCPCS code
            setting: 'facility' or 'non-facility'
            work_gpci: Work GPCI for locality
            pe_gpci: Practice Expense GPCI
            mp_gpci: Malpractice GPCI
            modifier: Modifier code if applicable
        
        Returns:
            Dictionary with RVU components and payment amount
        """
        record = self.get_record(hcpcs_code, modifier)
        if not record:
            return None
        
        if not record.conversion_factor:
            return None
        
        # Select PE RVU based on setting
        pe_rvu = record.fac_pe_rvu if setting == 'facility' else record.non_fac_pe_rvu
        
        if not all([record.work_rvu, pe_rvu, record.mp_rvu]):
            return None
        
        # Calculate adjusted RVUs
        adj_work = record.work_rvu * work_gpci
        adj_pe = pe_rvu * pe_gpci
        adj_mp = record.mp_rvu * mp_gpci
        
        total_adj_rvu = adj_work + adj_pe + adj_mp
        payment = total_adj_rvu * record.conversion_factor
        
        return {
            'hcpcs_code': hcpcs_code,
            'modifier': modifier,
            'description': record.description,
            'setting': setting,
            'work_rvu': float(record.work_rvu),
            'pe_rvu': float(pe_rvu),
            'mp_rvu': float(record.mp_rvu),
            'total_rvu': float(record.work_rvu + pe_rvu + record.mp_rvu),
            'work_gpci': float(work_gpci),
            'pe_gpci': float(pe_gpci),
            'mp_gpci': float(mp_gpci),
            'adjusted_work_rvu': float(adj_work),
            'adjusted_pe_rvu': float(adj_pe),
            'adjusted_mp_rvu': float(adj_mp),
            'total_adjusted_rvu': float(total_adj_rvu),
            'conversion_factor': float(record.conversion_factor),
            'payment_amount': float(payment)
        }


def download_cms_rvu_file(year: int = 2025, quarter: str = 'A') -> Optional[bytes]:
    """
    Download CMS RVU file
    
    Args:
        year: Year (e.g., 2025)
        quarter: Quarter (A=Jan, B=Apr, C=Jul, D=Oct)
    
    Returns:
        Zip file contents as bytes
    """
    # CMS URL pattern - this may need adjustment based on actual CMS URLs
    url = f"https://www.cms.gov/Medicare/Medicare-Fee-for-Service-Payment/PhysicianFeeSched/Downloads/RVU{str(year)[-2:]}{quarter}.zip"
    
    print(f"Attempting to download from: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return response.content
        else:
            print(f"Failed to download: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"Download error: {e}")
        return None


def extract_and_parse_zip(zip_content: bytes, parser: CMSRVUParser) -> bool:
    """Extract and parse RVU file from zip"""
    try:
        with zipfile.ZipFile(io.BytesIO(zip_content)) as zf:
            # Look for the main RVU file
            for name in zf.namelist():
                if 'PPRRVU' in name.upper() or name.endswith('.txt'):
                    print(f"Extracting and parsing: {name}")
                    content = zf.read(name)
                    
                    # Write to temp file and parse
                    temp_path = Path('/tmp/rvu_temp.txt')
                    with open(temp_path, 'wb') as f:
                        f.write(content)
                    
                    count = parser.parse_file(temp_path)
                    print(f"Parsed {count} records")
                    return count > 0
                    
                elif name.endswith('.csv'):
                    print(f"Extracting and parsing CSV: {name}")
                    content = zf.read(name)
                    temp_path = Path('/tmp/rvu_temp.csv')
                    with open(temp_path, 'wb') as f:
                        f.write(content)
                    
                    count = parser.parse_csv_file(temp_path)
                    print(f"Parsed {count} records from CSV")
                    return count > 0
                    
        return False
    except Exception as e:
        print(f"Error extracting zip: {e}")
        return False


if __name__ == "__main__":
    # Example usage
    parser = CMSRVUParser()
    
    # Try to download and parse latest file
    print("Downloading CMS RVU file...")
    zip_data = download_cms_rvu_file(2025, 'D')
    
    if zip_data:
        success = extract_and_parse_zip(zip_data, parser)
        if success:
            print(f"\nSuccessfully loaded {len(parser.records)} RVU records")
            
            # Example queries
            print("\n=== Sample Bronchoscopy Codes ===")
            bronch_codes = ['31622', '31623', '31624', '31625', '31626', '31628', '31629']
            for code in bronch_codes:
                record = parser.get_record(code)
                if record:
                    print(f"\n{code}: {record.description}")
                    print(f"  Work RVU: {record.work_rvu}")
                    print(f"  Non-Fac PE RVU: {record.non_fac_pe_rvu}")
                    print(f"  Fac PE RVU: {record.fac_pe_rvu}")
                    print(f"  MP RVU: {record.mp_rvu}")
                    print(f"  Total RVU (Non-Fac): {record.total_non_fac_rvu}")
                    
                    # Calculate payment (national average)
                    payment = parser.calculate_payment(code, setting='facility')
                    if payment:
                        print(f"  Payment (Facility): ${payment['payment_amount']:.2f}")
    else:
        print("Could not download RVU file from CMS")
