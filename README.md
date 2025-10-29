# MCP-KE

MCP server that wraps domain-specific tools.

## Quick Start

```bash
git clone <repo-url>
cd MCP-KE
pip install -e .
python ke_mcp/src/server.py
```

## How It Works

```
┌─────────────────────────────────────────┐
│ Your Multi-Agent System (MAS)          │
└─────────────────────────────────────────┘
                    ↓ MCP Protocol
┌─────────────────────────────────────────┐
│ MCP-KE Server                           │
│  - Reads config.yaml                    │
│  - Validates parameters                 │
│  - Routes to team tools                 │
└─────────────────────────────────────────┘
          ↓                    ↓
┌──────────────────┐  ┌──────────────────┐
│ Team A's Repo    │  │ Team B's Repo    │
│ (They Maintain)  │  │ (They Maintain)  │
│                  │  │                  │
│ drmacs.run()     │  │ drhacc.run()     │
└──────────────────┘  └──────────────────┘
```

## Available Tools

| Tool | Repository | Purpose | Contact |
|------|------------|---------|---------|
| drmacs | https://github.com/StarNetLaboratory/drmacs | SDSS astronomical data analysis | starnet-lab@example.com |
| drhacc | https://github.com/StarNetLaboratory/DrHACC | HACC simulation data analysis | starnet-lab@example.com |

## Add Your Tool

See [CONTRIBUTING.md](CONTRIBUTING.md)

MIT License
