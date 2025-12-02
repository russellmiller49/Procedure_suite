"""
RVU Calculator for Procedure Suite
Wraps CMS parser with project-specific functionality
"""

from pathlib import Path
from typing import Dict, List, Optional
from decimal import Decimal

import pandas as pd

from proc_autocode.ip_kb.ip_kb import IPCodingKnowledgeBase, CmsRvuInfo
from .rvu_parser import GPCIRecord


class ProcedureRVUCalculator:
    """RVU calculator backed by the IP knowledge base CMS tables."""
    
    def __init__(self, knowledge_base: IPCodingKnowledgeBase, gpci_file: Path | None = None):
        self.knowledge_base = knowledge_base
        self.conversion_factor = self.knowledge_base.get_conversion_factor() or 0.0
        self.gpci_data = self._load_gpci(gpci_file) if gpci_file else {}
        
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

    def _get_gpci(self, locality: str) -> Optional[GPCIRecord]:
        if not self.gpci_data:
            return None
        key = (locality or "00").zfill(2)
        return self.gpci_data.get(key) or self.gpci_data.get("00")

    @staticmethod
    def _dec(value: Optional[float]) -> Decimal:
        if value is None:
            return Decimal("0")
        return Decimal(str(value))
    
    def calculate_procedure_rvu(
        self,
        cpt_code: str,
        locality: str = "00",
        setting: str = "facility",
        modifiers: Optional[List[str]] = None,
    ) -> Optional[Dict]:
        """
        Calculate RVU and payment for a procedure using CMS data embedded in the knowledge base.
        """
        info = self.knowledge_base.get_cms_rvu(cpt_code)
        if not info:
            return None

        gpci = self._get_gpci(locality)
        facility_setting = (setting or "facility").lower() != "nonfacility"

        work = self._dec(info.work_rvu)
        mp = self._dec(info.mp_rvu)
        pe_source = info.facility_pe_rvu if facility_setting else info.nonfacility_pe_rvu
        if pe_source is None and info.facility_pe_rvu is not None:
            pe_source = info.facility_pe_rvu
        pe = self._dec(pe_source)

        base_total = work + pe + mp
        total = base_total
        if gpci:
            total = (work * gpci.work_gpci) + (pe * gpci.pe_gpci) + (mp * gpci.mp_gpci)

        cf = Decimal(str(self.conversion_factor or 0))
        if cf == 0:
            fallback = info.mpfs_facility_payment if facility_setting else info.mpfs_nonfacility_payment
            if fallback and total:
                cf = Decimal(str(fallback)) / total

        if cf == 0 and total:
            # If conversion factor is unknown, back-calculate from mpfs totals when available.
            fallback_total = info.mpfs_facility_payment if facility_setting else info.mpfs_nonfacility_payment
            payment_amount = float(fallback_total) if fallback_total is not None else float(total)
        else:
            payment_amount = float(total * cf)

        result = {
            "cpt_code": info.code,
            "description": info.description or f"CPT {info.code}",
            "work_rvu": float(info.work_rvu or 0.0),
            "pe_rvu": float(pe_source or 0.0) if pe_source is not None else 0.0,
            "mp_rvu": float(info.mp_rvu or 0.0),
            "total_rvu": float(total),
            "total_adjusted_rvu": float(total),
            "payment_amount": payment_amount,
            "setting": "facility" if facility_setting else "nonfacility",
            "locality": locality,
            "conversion_factor": float(cf),
            "category": info.category,
            "status_code": info.status_code,
            "global_days": info.global_days,
        }

        if modifiers:
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
                total_rvu_value = Decimal(str(result.get("total_adjusted_rvu", result.get("total_rvu", 0.0))))
                proc_total_rvu = float(total_rvu_value * Decimal(str(multiplier)))
                
                total_wrvu += proc_wrvu
                total_payment += proc_payment
                
                breakdown.append({
                    'cpt_code': proc['cpt_code'],
                    'work_rvu': float(proc_wrvu),
                    'total_rvu': proc_total_rvu,
                    'payment': proc_payment,
                    'multiplier': float(multiplier)
                })
        
        return {
            'total_work_rvu': float(total_wrvu),
            'total_payment': total_payment,
            'procedure_count': len(procedures),
            'breakdown': breakdown,
            'conversion_factor': self.conversion_factor,
        }
