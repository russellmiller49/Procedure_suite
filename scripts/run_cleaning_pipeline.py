#!/usr/bin/env python
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--validate-kb', action='store_true')
    parser.add_argument('--autopatch', action='store_true')
    args = parser.parse_args()
    try:
        from modules.registry_cleaning.pipeline import run_pipeline
    except Exception as e:
        print(f"Could not import run_pipeline: {e}")
        return
    run_pipeline()

if __name__ == '__main__':
    main()
