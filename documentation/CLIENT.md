## Using with an MCP Client

We show an example of how MCP server setup can be used with a client. Example here is with Claude Desktop to give Claude access to all the analysis tools.

### Setup

**1. Install the package**
```bash
cd /path/to/hep-ke/mcp
pip install -e .
```

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

Claude will automatically:
- Launch the MCP server as a subprocess
- Discover all 20+ tools
- Make them available in conversations

**4. Verify**

Ask Claude: "Can you list the available tools from mcp-ke?"

### Usage Example

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