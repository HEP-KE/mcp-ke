#!/usr/bin/env python3
"""Test that MCP tool schemas are generated correctly."""

import sys
import inspect
from mcp_server import build_mcp_tool, discover_tools

# Discover all tools
tools_dict = discover_tools()

print("=" * 80)
print("MCP Tool Schema Test")
print("=" * 80)

# Test a few key tools
test_tools = ['nu_mass', 'wCDM', 'LCDM', 'compute_power_spectrum', 'compute_suppression_ratios']

for tool_name in test_tools:
    if tool_name not in tools_dict:
        print(f"\n❌ Tool '{tool_name}' not found!")
        continue

    func = tools_dict[tool_name]
    mcp_tool = build_mcp_tool(tool_name, func)

    print(f"\n{'=' * 80}")
    print(f"Tool: {tool_name}")
    print(f"{'=' * 80}")

    # Get the actual function signature
    actual_func = func.forward if hasattr(func, 'forward') else func
    sig = inspect.signature(actual_func)

    print(f"Function signature: {sig}")
    print(f"\nMCP Tool Schema:")
    print(f"  Name: {mcp_tool.name}")
    print(f"  Description: {mcp_tool.description[:100]}...")
    print(f"  Input Schema:")
    print(f"    Properties: {list(mcp_tool.inputSchema['properties'].keys())}")
    print(f"    Required: {mcp_tool.inputSchema['required']}")

    # Detailed parameter info
    print(f"\n  Parameters:")
    for param_name, param_schema in mcp_tool.inputSchema['properties'].items():
        required = "required" if param_name in mcp_tool.inputSchema['required'] else "optional"
        print(f"    - {param_name}: {param_schema['type']} ({required})")

print(f"\n{'=' * 80}")
print("Test Complete")
print(f"{'=' * 80}")
