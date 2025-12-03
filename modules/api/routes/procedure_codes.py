from fastapi import APIRouter, HTTPException
from typing import List
from modules.proc_autocode.models import CodeSuggestion, FinalCode, ReviewAction

router = APIRouter()

# In-memory stores for demonstration; in real implementation use DB or Supabase.
procedure_code_suggestions: dict[str, List[CodeSuggestion]] = {}
procedure_code_reviews: dict[str, List[ReviewAction]] = {}
procedure_codes_final: dict[str, List[FinalCode]] = {}

@router.post("/procedures/{proc_id}/codes/ai", response_model=List[CodeSuggestion])
def run_ai_coder(proc_id: str):
    """Trigger the AI coding pipeline for a procedure and store suggestions."""
    # TODO: call your actual coding pipeline here
    suggestions: List[CodeSuggestion] = []
    procedure_code_suggestions[proc_id] = suggestions
    return suggestions

@router.get("/procedures/{proc_id}/codes/ai", response_model=List[CodeSuggestion])
def get_ai_suggestions(proc_id: str):
    """Retrieve AI code suggestions for a procedure."""
    return procedure_code_suggestions.get(proc_id, [])

@router.post("/procedures/{proc_id}/codes/review")
def post_review(proc_id: str, reviews: List[ReviewAction]):
    """Submit review actions and update final codes accordingly."""
    procedure_code_reviews.setdefault(proc_id, []).extend(reviews)
    finals: List[FinalCode] = []
    for review in reviews:
        if review.final_code:
            procedure_codes_final.setdefault(proc_id, []).append(review.final_code)
            finals.append(review.final_code)
    return {"final_codes": finals}

@router.post("/procedures/{proc_id}/codes/manual")
def post_manual_code(proc_id: str, codes: List[FinalCode]):
    """Add manual codes to the final codes list."""
    procedure_codes_final.setdefault(proc_id, []).extend(codes)
    return {"final_codes": codes}

@router.get("/procedures/{proc_id}/codes/final", response_model=List[FinalCode])
def get_final_codes(proc_id: str):
    """Retrieve clinician-approved final codes for a procedure."""
    return procedure_codes_final.get(proc_id, [])
