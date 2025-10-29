# MCP-KE

MCP server that serves cosmology analysis tools.

## Quick Start

```bash
pip install -e .
python mcp_server.py
```

## Available Tools

### Data & Models
- `load_observational_data`: Load BOSS galaxy power spectrum data
- `LCDM`, `nu_mass`, `wCDM`: Cosmology models

### Analysis & Visualization
- `compute_power_spectrum`, `compute_all_models`, `compute_suppression_ratios`
- `plot_power_spectra`, `plot_suppression_ratios`

### Agent Helpers
- `list_agent_files`, `save_array`, `load_array`, `save_dict`, `load_dict`

## Add Your Tool

See [CONTRIBUTING.md](CONTRIBUTING.md)

MIT License
