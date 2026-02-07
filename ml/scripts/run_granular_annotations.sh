#!/bin/bash
# Run all granular annotation scripts to generate Excel files
# Output goes to data/granular annotations/phase0_excels/

# Don't use set -e because arithmetic expressions can return non-zero

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
GRANULAR_DIR="$PROJECT_ROOT/data/granular annotations"
PYTHON_SCRIPTS_DIR="$GRANULAR_DIR/python scripts"
OUTPUT_DIR="$GRANULAR_DIR/phase0_excels"

echo "=== Granular Annotation Script Runner ==="
echo "Project root: $PROJECT_ROOT"
echo "Scripts dir: $PYTHON_SCRIPTS_DIR"
echo "Output dir: $OUTPUT_DIR"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Count scripts
SCRIPT_COUNT=$(ls -1 "$PYTHON_SCRIPTS_DIR"/Granular_note_*.py 2>/dev/null | wc -l)
echo "Found $SCRIPT_COUNT annotation scripts"
echo ""

# Change to granular annotations dir (so template path resolves correctly)
cd "$GRANULAR_DIR"

# Track progress
SUCCESS=0
FAILED=0

# Run each script
for script in "$PYTHON_SCRIPTS_DIR"/Granular_note_*.py; do
    script_name=$(basename "$script")
    note_id=$(echo "$script_name" | sed 's/Granular_note_\([0-9]*\)\.py/note_\1/')
    output_file="phase0_extraction_${note_id}.xlsx"

    echo -n "Processing $script_name... "

    if python "$script" 2>/dev/null; then
        # Move output to phase0_excels/
        if [ -f "$output_file" ]; then
            mv "$output_file" "$OUTPUT_DIR/"
            echo "OK"
            ((SUCCESS++))
        else
            echo "WARN: No output file generated"
            ((FAILED++))
        fi
    else
        echo "FAILED"
        ((FAILED++))
    fi
done

echo ""
echo "=== Complete ==="
echo "Success: $SUCCESS"
echo "Failed: $FAILED"
echo "Output directory: $OUTPUT_DIR"
