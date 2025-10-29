#!/usr/bin/env python3
"""Validate config.yaml schema"""
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml
from ke_mcp.src.config_loader import get_config_path
from ke_mcp.src.config_validator import validate_config_structure


def main() -> bool:
    """Validate config.yaml and report errors"""
    try:
        with open(get_config_path()) as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"❌ Config not found: {get_config_path()}", file=sys.stderr)
        return False
    except yaml.YAMLError as e:
        print(f"❌ Invalid YAML: {e}", file=sys.stderr)
        return False

    errors = validate_config_structure(config)

    if errors:
        print("❌ Config validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return False

    tool_count = len(config.get("tools", {}))
    print(f"✓ Config validation passed ({tool_count} tools)")
    return True


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
