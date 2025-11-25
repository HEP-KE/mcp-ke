# MCP-KE

Model Context Protocol (MCP) server providing cosmology analysis tools for LLM agents.

## What is MCP-KE?

An MCP server that exposes 20+ tools for cosmological analysis:
- **Domain Tools**: Load data, compute power spectra, create visualizations
- **Agent Tools**: AI-powered workflows for complex multi-step analysis

## Documentation

- **[DESIGN.md](DESIGN.md)**: Architecture, design rationale, and technical details
- **[CONTRIBUTING.md](documentation/CONTRIBUTING.md)**: Guide for adding new tools

## Quick Start

```bash
# Install
pip install -e .

# Run server (for testing)
python mcp_server.py
```

## Available Tools

### Domain Tools (16 tools)

**Data & Models**
- `load_observational_data` - Load eBOSS observational data
- `LCDM`, `nu_mass`, `wCDM` - Cosmology model parameter sets
- `create_theory_k_grid` - Generate k-value grid for theory predictions

**Analysis**
- `compute_power_spectrum` - Compute P(k) for given parameters using CLASS
- `compute_all_models` - Compute P(k) for all standard models
- `compute_suppression_ratios` - Calculate P(k)/P_ref(k) ratios

**Visualization**
- `plot_power_spectra` - Plot P(k) vs observations
- `plot_suppression_ratios` - Plot suppression ratios

**Helpers**
- `save_array`, `load_array`, `save_dict`, `load_dict`, `list_agent_files`

### Agent Tools (2 tools)

Require OpenAI-compatible LLM API (Anthropic, Google Gemini, OpenAI, etc.)

**`power_spectrum_agent`**
- End-to-end power spectrum analysis workflow
- Orchestrates: data agent → modeling agent → visualization agent
- Example:
  ```python
  result = power_spectrum_agent(
      query="Compare ΛCDM and wCDM models with eBOSS data",
      api_key="your-key",
      llm_url="https://api.anthropic.com",
      model_id="claude-3-5-sonnet-20241022"
  )
  ```

**`arxiv_agent`**
- Search arXiv, download papers, extract and analyze content
- Example:
  ```python
  result = arxiv_agent(
      query="Find recent papers on galaxy mass estimation methods",
      api_key="your-key",
      llm_url="https://api.anthropic.com",
      model_id="claude-3-5-sonnet-20241022"
  )
  ```



## Testing

```bash
# Unit tests (no API key needed)
pytest

# Integration tests (requires GOOGLE_API_KEY)
export GOOGLE_API_KEY="your-key"
pytest tests/test_agent_tools.py -v
```

## Contributing

See [CONTRIBUTING.md](documentation/CONTRIBUTING.md)

MIT License