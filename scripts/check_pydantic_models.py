#!/usr/bin/env python
import importlib
import sys

def main():
    modules = [
        'proc_schemas.envelope_models',
    ]
    for m in modules:
        try:
            importlib.import_module(m)
            print(f"{m} imported successfully")
        except Exception as e:
            print(f"Failed to import {m}: {e}")
            sys.exit(1)

if __name__ == '__main__':
    main()
