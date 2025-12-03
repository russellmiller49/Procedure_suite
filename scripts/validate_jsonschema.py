#!/usr/bin/env python
import json
import pathlib
import sys
import jsonschema

def load_schema(schema_path):
    with open(schema_path) as f:
        return json.load(f)

def validate_schema():
    root = pathlib.Path(__file__).resolve().parent.parent
    schema_file = root / 'schemas' / 'IP_Registry_Enhanced_v2.json'
    if not schema_file.exists():
        print(f"Schema file not found: {schema_file}")
        return
    schema = load_schema(schema_file)
    try:
        jsonschema.Draft7Validator.check_schema(schema)
        print("Schema is valid")
    except Exception as e:
        print(f"Schema validation error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    validate_schema()
