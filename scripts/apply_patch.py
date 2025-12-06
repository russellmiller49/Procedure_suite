import json
import jsonpatch

ORIGINAL_PATH = "data/unpatched_goldens/consolidated_verified_notes_v2_8_part_004.json"
PATCH_PATH = "data/knowledge/golden_patches/consolidated_verified_notes_v2_8_part_004_patch.json"
OUTPUT_PATH = "data/knowledge/golden_extractions/consolidated_verified_notes_v2_8_part_004_patch.json"

def main():
    # load original notes
    with open(ORIGINAL_PATH, "r", encoding="utf-8") as f:
        original = json.load(f)

    # load JSON Patch operations
    with open(PATCH_PATH, "r", encoding="utf-8") as f:
        patch_ops = json.load(f)

    # apply patch
    patch = jsonpatch.JsonPatch(patch_ops)
    patched = patch.apply(original, in_place=False)

    # write patched file
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(patched, f, indent=2)

    print(f"Patched file written to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
