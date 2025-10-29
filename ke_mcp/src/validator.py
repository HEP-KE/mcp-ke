"""Tool validation utilities"""
import sys
from ke_mcp.src import invoke, config_loader


def validate_all_tools() -> tuple[bool, list[str]]:
    """
    Validate all configured tools can be loaded.

    Returns: (success, error_messages)
    """
    errors = []
    tools = config_loader.get_all_tools()

    for tool_id, tool_config in tools.items():
        entry_point = tool_config.get("entry_point")
        if not entry_point:
            errors.append(f"{tool_id}: Missing 'entry_point' in config")
            continue

        is_valid, error_msg = invoke.validate_entry_point(entry_point)
        if not is_valid:
            errors.append(f"{tool_id} ({entry_point}): {error_msg}")

    return len(errors) == 0, errors


def validate_or_exit():
    """Validate tools and exit if any fail"""
    success, errors = validate_all_tools()

    if not success:
        print("❌ Tool validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        print("\nInstall tools: pip install -r requirements.txt", file=sys.stderr)
        sys.exit(1)

    tool_count = len(config_loader.get_all_tools())
    print(f"✓ Validated {tool_count} tools", file=sys.stderr)
