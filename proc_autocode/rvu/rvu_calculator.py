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
                
                proc_payment = result['payment_amount'] * float(multiplier)
                proc_wrvu = Decimal(str(result['work_rvu'])) * Decimal(str(multiplier))
                
                total_wrvu += proc_wrvu
                total_payment += proc_payment
                
                breakdown.append({
                    'cpt_code': proc['cpt_code'],
                    'work_rvu': float(proc_wrvu),
                    'payment': proc_payment,
                    'multiplier': float(multiplier)
                })
        
        return {
            'total_work_rvu': float(total_wrvu),
            'total_payment': total_payment,
            'procedure_count': len(procedures),
            'breakdown': breakdown
        }
