#!/usr/bin/env python
"""Validate YAML workflow files"""
import yaml
import sys
from pathlib import Path


def validate_yaml_file(filepath):
    """Validate a single YAML file"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            yaml.safe_load(f)
        return True, None
    except yaml.YAMLError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)


def main():
    workflows_dir = Path(".github/workflows")
    yaml_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))

    print("=" * 60)
    print("YAML VALIDATION REPORT")
    print("=" * 60)
    print()

    all_valid = True
    for yaml_file in yaml_files:
        valid, error = validate_yaml_file(yaml_file)
        status = "[VALID]" if valid else "[INVALID]"
        print(f"{status}: {yaml_file}")
        if error:
            print(f"  Error: {error}")
            all_valid = False

    print()
    if all_valid:
        print("[PASS] All YAML files are valid!")
        return 0
    else:
        print("[FAIL] Some YAML files have errors!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
