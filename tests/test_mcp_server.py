"""Test MCP server tool discovery and basic functionality."""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server import discover_tools, build_mcp_tool


def test_tool_discovery():
    """Test that tools are discovered from both tools/ and agent_tools/."""
    tools = discover_tools()

    # Check we have tools
    assert len(tools) > 0, "No tools were discovered"

    # Check for expected domain tools
    expected_domain_tools = [
        'load_observational_data',
        'LCDM',
        'compute_power_spectrum',
        'plot_power_spectra'
    ]

    for tool_name in expected_domain_tools:
        assert tool_name in tools, f"Expected domain tool '{tool_name}' not found"

    # Check for expected agent tools
    expected_agent_tools = [
        'power_spectrum_agent',
        'arxiv_agent'
    ]

    for tool_name in expected_agent_tools:
        assert tool_name in tools, f"Expected agent tool '{tool_name}' not found"


def test_tool_attributes():
    """Test that discovered tools have required attributes."""
    tools = discover_tools()

    for name, tool_func in tools.items():
        # Check tool is callable
        assert callable(tool_func), f"Tool '{name}' is not callable"

        # Check tool has name attribute (from smolagents decorator)
        assert hasattr(tool_func, 'name'), f"Tool '{name}' missing 'name' attribute"


def test_mcp_tool_conversion():
    """Test that tools can be converted to MCP Tool format."""
    tools = discover_tools()

    # Test with a simple domain tool
    if 'LCDM' in tools:
        mcp_tool = build_mcp_tool('LCDM', tools['LCDM'])

        assert mcp_tool.name == 'LCDM'
        assert mcp_tool.description is not None
        assert mcp_tool.inputSchema is not None
        assert 'type' in mcp_tool.inputSchema
        assert 'properties' in mcp_tool.inputSchema


def test_agent_tool_discovery():
    """Test that agent tools are properly discovered."""
    tools = discover_tools()

    # Check specific agent tools exist
    assert 'power_spectrum_agent' in tools
    assert 'arxiv_agent' in tools

    # Verify they're callable
    assert callable(tools['power_spectrum_agent'])
    assert callable(tools['arxiv_agent'])


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
