#!/usr/bin/env python3
"""Generate requirements.txt from config.yaml"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ke_mcp.src.config_loader import get_all_tools


def main():
    """Generate requirements.txt with tool dependencies"""
    tools = get_all_tools()

    repos = []
    for tool_config in tools.values():
        repo = tool_config["repository"]
        version = tool_config.get("version", "main")
        repos.append(f"git+{repo}.git@{version}")

    requirements = f"""# MCP-KE Core Dependencies
mcp>=0.9.0
pyyaml>=6.0

# Team Tools (pinned to specific versions)
{chr(10).join(repos)}
"""

    output_path = Path(__file__).parent.parent / "requirements.txt"
    output_path.write_text(requirements)
    print("✓ Generated requirements.txt")


if __name__ == "__main__":
    main()
