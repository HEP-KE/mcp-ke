"""Test agent tools for basic functionality.

Integration tests require LLM environment variables:
    export LLM_API_KEY="your-api-key"
    export LLM_URL="https://generativelanguage.googleapis.com/v1beta/openai/"
    export LLM_MODEL="gemini-2.0-flash-exp"
"""

import pytest
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_tools import create_openai_compatible_llm
from agent_tools.arxiv_agent import arxiv_agent
# Import power_spectrum_agent directly from its module since it's disabled in __init__.py
from agent_tools.power_spectrum_agent import power_spectrum_agent

# Check if we can run integration tests
LLM_API_KEY = os.getenv('LLM_API_KEY')
LLM_URL = os.getenv('LLM_URL')
LLM_MODEL = os.getenv('LLM_MODEL')
CAN_RUN_INTEGRATION = all([LLM_API_KEY, LLM_URL, LLM_MODEL])


def test_create_openai_compatible_llm_validation():
    """Test LLM helper validates required parameters."""

    # Test missing api_key
    with pytest.raises(ValueError, match="api_key"):
        create_openai_compatible_llm("", "https://api.anthropic.com", "claude-3-5-sonnet-20241022")

    # Test missing llm_url
    with pytest.raises(ValueError, match="llm_url"):
        create_openai_compatible_llm("test-key", "", "claude-3-5-sonnet-20241022")

    # Test missing model_id
    with pytest.raises(ValueError, match="model_id"):
        create_openai_compatible_llm("test-key", "https://api.anthropic.com", "")


def test_agent_tools_are_callable():
    """Test that agent tools are callable."""
    assert callable(power_spectrum_agent)
    assert callable(arxiv_agent)


def test_agent_tools_have_names():
    """Test that agent tools have name attributes."""
    assert hasattr(power_spectrum_agent, 'name')
    assert hasattr(arxiv_agent, 'name')

    assert power_spectrum_agent.name == 'power_spectrum_agent'
    assert arxiv_agent.name == 'arxiv_agent'


def test_power_spectrum_agent_missing_env_vars():
    """Test power spectrum agent handles missing environment variables."""
    # Save and clear env vars
    saved_vars = {
        'LLM_API_KEY': os.environ.pop('LLM_API_KEY', None),
        'LLM_URL': os.environ.pop('LLM_URL', None),
        'LLM_MODEL': os.environ.pop('LLM_MODEL', None),
    }

    try:
        result = power_spectrum_agent(query="test query")

        # Should return error message about missing env vars
        assert isinstance(result, str)
        assert "error" in result.lower() or "missing" in result.lower()
    finally:
        # Restore env vars
        for key, value in saved_vars.items():
            if value is not None:
                os.environ[key] = value


def test_arxiv_agent_missing_env_vars():
    """Test arxiv agent handles missing environment variables."""
    # Save and clear env vars
    saved_vars = {
        'LLM_API_KEY': os.environ.pop('LLM_API_KEY', None),
        'LLM_URL': os.environ.pop('LLM_URL', None),
        'LLM_MODEL': os.environ.pop('LLM_MODEL', None),
    }

    try:
        result = arxiv_agent(query="test query")

        # Should return error message about missing env vars
        assert isinstance(result, str)
        assert "error" in result.lower() or "missing" in result.lower()
    finally:
        # Restore env vars
        for key, value in saved_vars.items():
            if value is not None:
                os.environ[key] = value


def test_agent_tools_have_descriptions():
    """Test that agent tools have proper descriptions."""
    # Check power_spectrum_agent
    ps_desc = getattr(power_spectrum_agent, 'description', None) or power_spectrum_agent.__doc__
    assert ps_desc is not None
    assert len(ps_desc) > 50, "power_spectrum_agent description too short"

    # Check arxiv_agent
    arxiv_desc = getattr(arxiv_agent, 'description', None) or arxiv_agent.__doc__
    assert arxiv_desc is not None
    assert len(arxiv_desc) > 50, "arxiv_agent description too short"


def test_agent_tools_discoverable_by_mcp():
    """Test that agent tools are discovered by MCP server."""
    from mcp_server import discover_tools

    tools = discover_tools()

    # arxiv_agent should be discoverable (it's exported in __init__.py)
    assert 'arxiv_agent' in tools, "arxiv_agent not discovered by MCP"

    # power_spectrum_agent is commented out in __init__.py but should still be discovered
    # because discover_tools walks all modules
    assert 'power_spectrum_agent' in tools, "power_spectrum_agent not discovered by MCP"


@pytest.mark.skipif(not CAN_RUN_INTEGRATION, reason="LLM environment variables not set")
def test_arxiv_agent_integration():
    """Integration test: Run arxiv agent with real LLM."""
    result = arxiv_agent(
        query="Search for one recent paper on cosmology. Return the title and arxiv ID only."
    )

    # Check we got a string result
    assert isinstance(result, str)
    assert len(result) > 0

    # Check result doesn't contain fatal error (minor errors in paper download are ok)
    assert "missing environment variables" not in result.lower()


@pytest.mark.skipif(not CAN_RUN_INTEGRATION, reason="LLM environment variables not set")
def test_power_spectrum_agent_integration():
    """Integration test: Run power spectrum agent with real LLM."""
    result = power_spectrum_agent(
        query="Create a theory k-grid and compute power spectrum for LCDM model."
    )

    # Check we got a string result
    assert isinstance(result, str)
    assert len(result) > 0

    # Check result doesn't contain fatal error
    assert "missing environment variables" not in result.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
