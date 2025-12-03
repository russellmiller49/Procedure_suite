from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from proc_autocode.coder import EnhancedCPTCoder

router = APIRouter(prefix="/proc/enhanced", tags=["Enhanced Coder"])

# Initialize coder once (singleton-ish pattern for the module)
_coder = EnhancedCPTCoder()

class CodingRequest(BaseModel):
    text: str = Field(..., description="The procedure note or findings text.")
    locality: str = Field(default="00", description="Locality code (e.g., '00' for National, '05102' for San Diego). Use GET /proc/enhanced/localities to see options.")
    setting: str = Field(default="facility", description="Practice setting: 'facility' or 'non-facility'.")
    hints: Dict[str, Any] = Field(default_factory=dict, description="Optional hints for the coder.")

class LocalityInfo(BaseModel):
    code: str
    name: str

class EnhancedBillingResult(BaseModel):
    codes: List[Dict[str, Any]]
    total_work_rvu: float
    estimated_payment: float
    locality: str
    setting: str

@router.get("/localities", response_model=List[LocalityInfo])
def get_localities():
    """
    Returns a list of available localities for RVU adjustments.
    """
    localities = []
    for code, record in _coder.rvu_calc.gpci_data.items():
        localities.append(LocalityInfo(code=code, name=record.locality_name))
    
    # Sort by name for easier reading
    localities.sort(key=lambda x: x.name)
    return localities

@router.post("/code", response_model=EnhancedBillingResult)
def enhanced_code(payload: CodingRequest):
    """
    Enhanced auto-coding with RVU calculations and bundling rules.
    """
    procedure_data = {
        "note_text": payload.text,
        "locality": payload.locality,
        "setting": payload.setting,
        **payload.hints
    }
    
    try:
        result = _coder.code_procedure(procedure_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Coding error: {str(e)}")
