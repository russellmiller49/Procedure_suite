import json

# Load existing KB
with open('data/knowledge/ip_coding_billing_v2_8.json', 'r') as f:
    kb = json.load(f)

# Define missing codes identified in review
new_codes = {
    "32997": {
        "code": "32997",
        "description": "Total lung lavage (unilateral)",
        "family": "Intervention",
        "category": "Therapeutic"
    },
    "32662": {
        "code": "32662",
        "description": "Thoracoscopy, surgical; with excision of mediastinal cyst, tumor, or mass",
        "family": "Pleural",
        "category": "Surgical"
    },
    "33015": {
        "code": "33015",
        "description": "Tube pericardiostomy",
        "family": "Other",
        "category": "Pericardial"
    },
    "32602": {
        "code": "32602", # Note: Historical/Payer specific variant often seen in datasets
        "description": "Thoracoscopy, diagnostic with biopsy (Variant)", 
        "family": "Pleural",
        "category": "Diagnostic"
    }
}

# Update code_lists and hcpcs
for code, data in new_codes.items():
    if code not in kb.get('hcpcs', {}):
        kb.setdefault('hcpcs', {})[code] = data
        
    # Add 32997 to code_lists -> whole_lung_lavage if it exists, or create it
    if code == "32997":
        if "whole_lung_lavage" not in kb.get("code_lists", {}):
             kb["code_lists"]["whole_lung_lavage"] = []
        if code not in kb["code_lists"]["whole_lung_lavage"]:
            kb["code_lists"]["whole_lung_lavage"].append(code)

# Bump version
kb['version'] = "2.9"
kb['metadata']['label'] = "ip_coding_billing.v2.9"
kb['metadata']['changelog'].append("v2.9: Added missing codes from registry review (32997, 32662, 33015, 32602)")

# Save
with open('data/knowledge/ip_coding_billing_v2_9.json', 'w') as f:
    json.dump(kb, f, indent=2)

print("Created data/knowledge/ip_coding_billing_v2_9.json")