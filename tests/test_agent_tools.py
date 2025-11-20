"""Test agent tools for basic functionality.

Integration tests require GOOGLE_API_KEY environment variable:
    export GOOGLE_API_KEY="your-google-api-key"
"""

import pytest
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_tools import (
    create_openai_compatible_llm,
    power_spectrum_agent,
    arxiv_agent
)

# Gemini configuration for integration tests
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
GEMINI_MODEL = "gemini-2.0-flash-exp"

# Check if we can run integration tests
CAN_RUN_INTEGRATION = GOOGLE_API_KEY is not None


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


def test_analyze_power_spectrum_invalid_llm():
    """Test power spectrum agent handles invalid LLM configuration."""
    result = power_spectrum_agent(
        query="test query",
        api_key="",  # Invalid
        llm_url="https://api.anthropic.com",
        model_id="claude-3-5-sonnet-20241022"
    )

    # Should return error message, not crash
    assert isinstance(result, str)
    assert "error" in result.lower() or "configuration" in result.lower()


def test_run_arxiv_agent_invalid_llm():
    """Test arxiv agent handles invalid LLM configuration."""
    result = arxiv_agent(
        query="test query",
        api_key="",  # Invalid
        llm_url="https://api.anthropic.com",
        model_id="claude-3-5-sonnet-20241022"
    )

    # Should return error message, not crash
    assert isinstance(result, str)
    assert "error" in result.lower() or "configuration" in result.lower()


def test_analyze_power_spectrum_creates_directories():
    """Test that power spectrum agent creates required directories."""
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = os.path.join(tmpdir, "test_out")
        input_dir = os.path.join(tmpdir, "test_input")

        # Directories shouldn't exist yet
        assert not os.path.exists(output_dir)
        assert not os.path.exists(input_dir)

        # Run with invalid API key (won't actually run agent, but should create dirs)
        result = power_spectrum_agent(
            query="test",
            api_key="",
            llm_url="https://api.anthropic.com",
            model_id="test",
            output_dir=output_dir,
            input_dir=input_dir
        )

        # Directories should now exist
        assert os.path.exists(output_dir), "Output directory should be created"
        assert os.path.exists(input_dir), "Input directory should be created"


def test_run_arxiv_agent_creates_directory():
    """Test that arxiv agent creates output directory."""
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = os.path.join(tmpdir, "test_arxiv")

        # Directory shouldn't exist yet
        assert not os.path.exists(output_dir)

        # Run with invalid API key (won't actually run agent, but should create dir)
        result = arxiv_agent(
            query="test",
            api_key="",
            llm_url="https://api.anthropic.com",
            model_id="test",
            output_dir=output_dir
        )

        # Directory should now exist
        assert os.path.exists(output_dir), "Output directory should be created"


@pytest.mark.skipif(not CAN_RUN_INTEGRATION, reason="GOOGLE_API_KEY not set")
def test_arxiv_agent_integration():
    """Integration test: Run arxiv agent with real LLM."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        result = arxiv_agent(
            query="Search for one recent paper on cosmology. Return the title and arxiv ID only.",
            api_key=GOOGLE_API_KEY,
            llm_url=GEMINI_URL,
            model_id=GEMINI_MODEL,
            output_dir=tmpdir,
            max_steps=5  # Limit steps for faster test
        )

        # Check we got a string result
        assert isinstance(result, str)
        assert len(result) > 0

        # Check result doesn't contain error
        assert "error" not in result.lower() or "successfully" in result.lower()

        # Check some expected content (arxiv ID format or paper info)
        # Arxiv IDs look like: 2103.12345 or arxiv.org/abs/2103.12345
        assert "arxiv" in result.lower() or any(char.isdigit() for char in result)


@pytest.mark.skipif(not CAN_RUN_INTEGRATION, reason="GOOGLE_API_KEY not set")
def test_analyze_power_spectrum_integration():
    """Integration test: Run power spectrum agent with real LLM."""
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create required directories
        output_dir = os.path.join(tmpdir, "out")
        input_dir = os.path.join(tmpdir, "input")

        result = power_spectrum_agent(
            query="Create a theory k-grid and compute power spectrum for LCDM model.",
            api_key=GOOGLE_API_KEY,
            llm_url=GEMINI_URL,
            model_id=GEMINI_MODEL,
            output_dir=output_dir,
            input_dir=input_dir
        )

        # Check we got a string result
        assert isinstance(result, str)
        assert len(result) > 0

        # Check for expected content (file paths, success indicators, or model names)
        # Should mention files saved or LCDM or power spectrum
        result_lower = result.lower()
        success_indicators = [
            "lcdm" in result_lower,
            "power spectrum" in result_lower,
            "file" in result_lower,
            ".npy" in result_lower,
            "saved" in result_lower
        ]

        # At least one success indicator should be present
        assert any(success_indicators), f"Expected success indicators in result: {result[:200]}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
