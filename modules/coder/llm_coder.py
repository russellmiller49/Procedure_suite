from __future__ import annotations

import json
import re
from typing import List

from modules.common.llm import GeminiLLM
from .schema import LLMCodeSuggestion


def safe_extract_json(text: str) -> dict:
    """Reliably extract JSON object from text, handling markdown fences."""
    try:
        return json.loads(text)
    except Exception:
        # Try to find first { ... } block
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
    return {}


class LLMCoder:
    def __init__(self, model: str | None = None) -> None:
        self.llm = GeminiLLM(model=model or "gemini-2.5-flash")

    def suggest_codes(self, note_text: str) -> List[LLMCodeSuggestion]:
        prompt = f"""
You are an expert CPT coder specializing in interventional pulmonology and bronchoscopy.
You MUST return ONLY valid JSON and NOTHING else.

Your task:
- Read the bronchoscopy procedure note below.
- Identify all billable bronchoscopy CPT codes from the list provided.
- Return a JSON object with a single key: "codes".
- "codes" must be an array of objects.
- Each object must contain:
  - "cpt": the CPT code as a string
  - "description": short human-readable text
  - "rationale": evidence from the note supporting the code (1–3 sentences)

The ONLY codes you may choose from are:
31622, 31623, 31624, 31627, 31628, 31629, 31630,
31632, 31633, 31634, 31645, 31646, 31647,
31651, 31652, 31653, 31654, 32555,
99152, 99153

Rules:
- Do NOT return any explanations outside the JSON.
- Do NOT use markdown formatting.
- Do NOT include comments.
- Do NOT invent CPT codes.
- If a code is not clearly supported by explicit documentation, omit it.

Return EXACTLY this structure:

{{
  "codes": [
    {{
      "cpt": "31652",
      "description": "Linear EBUS-TBNA 1-2 stations",
      "rationale": "Station 11RS and 7 were sampled with convex probe EBUS."
    }}
  ]
}}

Now analyze this bronchoscopy note and produce the JSON ONLY.

NOTE:
{note_text}
"""
        
        # Strict schema enforcement for Gemini
        schema = {
            "type": "object",
            "properties": {
                "codes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "cpt": {"type": "string"},
                            "description": {"type": "string"},
                            "rationale": {"type": "string"}
                        },
                        "required": ["cpt", "description", "rationale"]
                    }
                }
            },
            "required": ["codes"]
        }

        try:
            raw = self.llm.generate(prompt, response_schema=schema)
            data = safe_extract_json(raw)
            
            if not data or "codes" not in data:
                return []
                
            codes = data.get("codes") or []
            return [LLMCodeSuggestion(**c) for c in codes if "cpt" in c]
        except Exception as e:
            # Log error or return empty
            return []