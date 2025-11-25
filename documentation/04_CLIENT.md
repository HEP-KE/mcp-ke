# Using MCP-KE with Clients

## Integration with Claude Desktop

We show how to set up the MCP server with a client (like Claude Desktop in this example to give Claude access to all cosmology analysis tools). 

### Setup Process

**1. Install MCP-KE**

```bash
cd /path/to/hep-ke/mcp
pip install -e .
```

This installs:
- Package `mcp-ke` with all dependencies
- Command `mcp-ke` (entry point to mcp_server:main)

**2. Configure Claude Desktop**

Create or edit: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "mcp-ke": {
      "command": "python",
      "args": [
        "/absolute/path/to/hep-ke/mcp/mcp_server.py"
      ],
      "env": {
        "GOOGLE_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

**Notes**:
- Replace `/absolute/path/to/` with your actual path
- `env.GOOGLE_API_KEY` is optional but required for agent tools (`power_spectrum_agent`, `arxiv_agent`)
- On Windows, config file is at: `%APPDATA%\Claude\claude_desktop_config.json`
- On Linux: `~/.config/Claude/claude_desktop_config.json`

**3. Restart Claude Desktop**

Claude Desktop will:
1. Read config on startup
2. Launch `python mcp_server.py` as subprocess
3. Attach stdin/stdout pipes
4. Call `list_tools()` to discover available tools
5. Make tools available in conversation

**4. Verify Connection**

In Claude Desktop, ask: "Can you list the available tools from mcp-ke?"

You should see all 23 tools listed.

### Usage Patterns

**Pattern 1: Direct Tool Usage**

User: "Load the eBOSS data from input/DR14_pm3d_19kbins.txt"

Claude calls: `load_observational_data("DR14_pm3d_19kbins.txt")`

**Pattern 2: Multi-Tool Workflow**

User: "Compare ΛCDM with massive neutrino model (0.1 eV) using eBOSS data"

Claude orchestrates:
1. `load_observational_data(...)`
2. `create_theory_k_grid()`
3. `LCDM()`
4. `nu_mass(0.1)`
5. `compute_power_spectrum(...)` for each model
6. `plot_power_spectra(...)`

**Pattern 3: Agent Tool Usage**

User: "Using the observational data from eBOSS, compare ΛCDM, massive neutrinos, and wCDM models"

Claude calls: `power_spectrum_agent(query="Compare ΛCDM, nu_mass, wCDM models with eBOSS data", api_key=os.getenv("GOOGLE_API_KEY"), ...)`

The agent tool handles the entire workflow internally and returns final analysis.

### Example Usage

```
You: Using the observational data from eBOSS DR14, compare the linear P(k)
     values for ΛCDM, ΛCDM with massive neutrinos, and dark energy model
     with equation of state parameter w0=-0.9. Comment on how close the P(k)
     values are and analyze the power spectrum suppression compared to ΛCDM.
```

Claude will use the tools to:
1. Load eBOSS data
2. Compute power spectra for each model
3. Create comparison visualizations
4. Provide detailed analysis

## Using with Other MCP Clients

MCP-KE follows the standard MCP protocol and can be used with any MCP-compatible client.

### General Setup

1. Configure your MCP client to launch `python /path/to/mcp_server.py`
2. Ensure the client uses stdio for communication
3. Set environment variables if using agent tools (GOOGLE_API_KEY, etc.)
4. Ensure working directory has `input/` with data files

### Custom Client Integration

If building your own MCP client:

```python
import subprocess
import json

# Launch MCP-KE server
process = subprocess.Popen(
    ["python", "/path/to/mcp_server.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    env={"GOOGLE_API_KEY": "your-key"}
)

# Send MCP protocol messages via stdin
# Read responses from stdout
# See MCP specification for details
```

## Tool Categories Available

### Domain Tools (10+ total)

**Data Loading**:
- `load_observational_data`: Load eBOSS DR14 data
- `create_theory_k_grid`: Generate k-space grid

**Model Parameters**:
- `LCDM`: Planck 2018 baseline cosmology
- `nu_mass`: ΛCDM with massive neutrinos
- `wCDM`: Dark energy with constant w

**Analysis**:
- `compute_power_spectrum`: Single model P(k)
- `compute_all_models`: Batch compute multiple models
- `compute_suppression_ratios`: P(k)/P_ref(k)

**Visualization**:
- `plot_power_spectra`: Two-panel comparison
- `plot_suppression_ratios`: Suppression ratio plot

**Utilities**:
- `save_array`, `load_array`: NumPy persistence
- `save_dict`, `load_dict`: JSON persistence
- `list_agent_files`: List output files

### Agent Tools (Currently 2)

**power_spectrum_agent**: Full cosmology analysis workflow
- 4-agent orchestration system
- Handles data loading, modeling, and visualization
- Returns complete analysis with plots

**arxiv_agent**: Literature search and paper analysis
- Searches arXiv database
- Downloads and extracts papers
- Provides summaries and citations


## Best Practices

1. **Start with domain tools**: Get familiar with individual tools before using agent tools
2. **Use agent tools for complex workflows**: Let agents handle multi-step orchestration
3. **Inspect output files**: Check `out/` directory for intermediate results
4. **Monitor API usage**: Agent tools make multiple LLM calls
5. **Keep data organized**: Use consistent naming in `input/` and `out/` directories
