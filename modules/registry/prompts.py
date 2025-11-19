"""Prompts for LLM-based registry extraction."""

from __future__ import annotations

def build_registry_prompt(note_text: str) -> str:
    return f"""You are an expert medical registry abstractor. Your job is to extract structured data from the provided procedure note.

Focus on extracting:
1. Lesions: Details about the pathology treated (e.g. stenosis, tumor).
2. Devices: All implants and tools used (stents, balloons, valves, catheters).
3. Technical Success: Was the procedure successful?
4. Complications.
5. Follow-up Plan.

Schema:
{{
  "lesions": [
    {{
      "type": "string (e.g. complex_tracheal_stenosis, tumor, malacia)",
      "location": "string (normalized airway segment)",
      "side": "left|right|midline|bilateral|null",
      "obstruction_baseline": "int (percentage)",
      "obstruction_post": "int (percentage)",
      "length_cm": "float",
      "distance_from_cords_cm": "float",
      "interventions": ["list of strings (stent, dilation, apc, etc.)"],
      "comments": "string"
    }}
  ],
  "devices": [
    {{
      "category": "stent|balloon|catheter|valve|other",
      "name": "string (e.g. Ultraflex, Elation, Zephyr)",
      "size_text": "string (e.g. 16x40mm, 14/16.5/18mm)",
      "location": "string",
      "details": {{ "key": "value" }}
    }}
  ],
  "technical_success": "complete|partial|failed|unknown",
  "complications": ["list of strings"],
  "followup_plan": "string"
}}

Example 1:
Note:
...Approximately 2.5 cm distal to the vocal cords was a long segment of circumferential complex stenosis measuring 3.5 cm with maximal airway obstruction of 90%... A 16x40 mm Ultraflex uncovered self-expandable metallic stent was then inserted... A 14/16.5/18 mm Elation dilatational balloon was used to dilate the stent after which the airway was approximately 90% of normal caliber.

Output:
{{
  "lesions": [
    {{
      "type": "complex_tracheal_stenosis",
      "location": "Trachea",
      "side": "midline",
      "obstruction_baseline": 90,
      "obstruction_post": 10,
      "length_cm": 3.5,
      "distance_from_cords_cm": 2.5,
      "interventions": ["stent", "dilation"]
    }}
  ],
  "devices": [
    {{
      "category": "stent",
      "name": "Ultraflex",
      "size_text": "16x40mm",
      "location": "Trachea",
      "details": {{ "type": "uncovered self-expandable metallic" }}
    }},
    {{
      "category": "balloon",
      "name": "Elation",
      "size_text": "14/16.5/18mm",
      "location": "Trachea",
      "details": {{ "type": "dilatational" }}
    }}
  ],
  "technical_success": "complete",
  "complications": [],
  "followup_plan": "Transfer to PACU. Discharge once criteria met. Plan for repeat evaluation and possible stent replacement in approximately 2 weeks."
}}

Task:
Extract the registry data from the following note. Return ONLY the JSON object.

Note:
{note_text}
"""
