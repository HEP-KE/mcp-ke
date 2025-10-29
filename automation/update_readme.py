#!/usr/bin/env python3
"""Generate README.md from config.yaml"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ke_mcp.src.config_loader import get_all_tools


def main():
    """Generate README with tool information"""
    tools = get_all_tools()

    table = "\n".join([
        f"| {tid} | {t['repository']} | {t['purpose']} | {t['contact']} |"
        for tid, t in tools.items()
    ])

    readme = f"""# MCP-KE

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
{table}

## Add Your Tool

See [CONTRIBUTING.md](CONTRIBUTING.md)

MIT License
"""

    output_path = Path(__file__).parent.parent / "README.md"
    output_path.write_text(readme)
    print("✓ Generated README.md")


if __name__ == "__main__":
    main()
