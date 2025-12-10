# Unified Deployment Guide - One Server for All Clients

## Overview

The **hybrid server** (`hybrid_server.py`) provides a single deployment that works with:
- ✅ **Claude Desktop** - via MCP SSE protocol
- ✅ **Claude Code** - via MCP SSE protocol
- ✅ **ChatGPT** - via REST API
- ✅ **Any MCP client** - via standard MCP protocol
- ✅ **Any REST client** - via OpenAPI-compatible REST API

**One URL, Multiple Protocols!**

---

## Quick Start

### Deploy to Fly.io (Recommended)

```bash
# Deploy the hybrid server
fly deploy

# Your server will be available at:
# https://your-app-name.fly.dev
```

That's it! The same server now handles both MCP and REST protocols.

---

## Client Configuration

### 1. Claude Desktop

**Steps:**
1. Open Claude Desktop
2. Click the settings/profile icon
3. Go to "Developer" → "Edit Config"
4. OR manually edit: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Add this configuration:**
```json
{
  "mcpServers": {
    "mcp-ke": {
      "command": "/usr/local/bin/python",
      "args": ["/path/to/mcp/mcp_server.py"]
    }
  }
}
```

**For Remote Server (Fly.io):**

As of the current Claude Desktop beta, URL-based connections may not be fully supported. If you see errors, use the local stdio method above. The UI shows URL support is coming soon.

**Workaround until URL support is stable:**
- Keep using local stdio connection
- Your tools will work the same way
- No need to keep Fly.io server running for Claude Desktop

---

### 2. Claude Code

Claude Code supports remote MCP servers via SSE.

**Edit `.claude/settings.json` in your project:**
```json
{
  "mcp_servers": {
    "mcp-ke": {
      "url": "https://your-app-name.fly.dev/sse"
    }
  }
}
```

**Or global config at `~/.config/claude-code/settings.json`**

---

### 3. ChatGPT (Custom GPT with Actions)

**Step 1: Create Custom GPT**
1. Go to https://chat.openai.com/gpts/editor
2. Click "Create a GPT"
3. Name it "Cosmology Analysis Assistant"

**Step 2: Configure Actions**
1. Click "Configure" tab
2. Scroll to "Actions" section
3. Click "Create new action"

**Step 3: Add OpenAPI Schema**

Get your schema from:
```
https://your-app-name.fly.dev/api/openapi.json
```

Or manually paste:
```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "MCP-KE Cosmology Tools",
    "description": "Tools for cosmology analysis including CLASS integration",
    "version": "1.0.0"
  },
  "servers": [
    {
      "url": "https://your-app-name.fly.dev"
    }
  ],
  "paths": {
    "/api/tools": {
      "get": {
        "summary": "List all available cosmology tools",
        "operationId": "listTools",
        "responses": {
          "200": {
            "description": "List of tools with descriptions"
          }
        }
      }
    },
    "/api/execute": {
      "post": {
        "summary": "Execute a cosmology analysis tool",
        "operationId": "executeTool",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "tool_name": {
                    "type": "string",
                    "description": "Name of the tool to execute (e.g., 'LCDM', 'compute_power_spectrum')"
                  },
                  "arguments": {
                    "type": "object",
                    "description": "Arguments to pass to the tool",
                    "additionalProperties": true
                  }
                },
                "required": ["tool_name"]
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Tool execution result"
          }
        }
      }
    }
  }
}
```

**Step 4: Add Instructions**

In the "Instructions" field, add:
```
You are a cosmology analysis assistant with access to tools for:
- Loading observational data from eBOSS
- Computing matter power spectra using CLASS
- Comparing different cosmological models (ΛCDM, wCDM, neutrino mass)
- Creating visualizations of power spectra

When users ask about cosmology, use the available tools to:
1. Load observational data when needed
2. Get model parameters (LCDM, nu_mass, wCDM)
3. Compute power spectra for analysis
4. Explain results in accessible language

Available tool names:
- LCDM, nu_mass, wCDM (get model parameters)
- load_observational_data (load eBOSS data)
- compute_power_spectrum (compute P(k) using CLASS)
- compute_all_models (compute multiple models)
- plot_power_spectra, plot_suppression_ratios (visualizations)
```

**Step 5: Test and Save**
1. Click "Test" to verify the action works
2. Try: "What are the ΛCDM parameters?"
3. Save your Custom GPT

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Hybrid Server (Fly.io)                    │
│                 https://your-app.fly.dev                     │
│                                                              │
│  ┌────────────────────┐      ┌──────────────────────┐       │
│  │   MCP Protocol     │      │     REST API         │       │
│  │   /sse             │      │     /api/*           │       │
│  │   /messages        │      │     /api/openapi.json│       │
│  └────────────────────┘      └──────────────────────┘       │
│           │                            │                     │
│           └────────────┬───────────────┘                     │
│                        │                                     │
│                  ┌─────▼──────┐                              │
│                  │  Tools (23) │                             │
│                  │  Discovery  │                             │
│                  └────────────┘                              │
└─────────────────────────────────────────────────────────────┘
         │                                │
         │                                │
  ┌──────▼────────┐              ┌───────▼──────────┐
  │ MCP Clients   │              │  REST Clients    │
  │ - Claude Desk │              │  - ChatGPT       │
  │ - Claude Code │              │  - Custom Apps   │
  └───────────────┘              └──────────────────┘
```

---

## Endpoints Reference

### MCP Endpoints (for Claude)

**SSE Stream:**
```
GET https://your-app.fly.dev/sse
```
Long-lived connection for MCP protocol communication.

**Messages:**
```
POST https://your-app.fly.dev/messages
```
For MCP message exchange.

### REST Endpoints (for ChatGPT)

**Root Info:**
```
GET https://your-app.fly.dev/
```
Returns server info and available protocols.

**List Tools:**
```
GET https://your-app.fly.dev/api/tools
```
Returns all 23 available tools with descriptions and parameters.

**Execute Tool:**
```
POST https://your-app.fly.dev/api/execute
Content-Type: application/json

{
  "tool_name": "LCDM",
  "arguments": {}
}
```

**OpenAPI Schema:**
```
GET https://your-app.fly.dev/api/openapi.json
```
Full OpenAPI 3.1 specification for ChatGPT Actions.

---

## Testing Your Deployment

### Test MCP Protocol (Claude)

```bash
# Test SSE endpoint
curl https://your-app.fly.dev/sse

# Should see SSE stream headers
```

### Test REST API (ChatGPT)

```bash
# List tools
curl https://your-app.fly.dev/api/tools

# Execute LCDM tool
curl -X POST https://your-app.fly.dev/api/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "LCDM", "arguments": {}}'

# Get OpenAPI schema
curl https://your-app.fly.dev/api/openapi.json
```

### Interactive Testing

Visit in browser:
```
https://your-app.fly.dev/
```

Shows server info and links to both protocols.

---

## Local Testing

### Run Hybrid Server Locally

```bash
python hybrid_server.py
```

Output:
```
Starting MCP-KE Hybrid Server...
Auto-discovering tools...
Discovered 23 tools: [...]

============================================================
Server listening on http://0.0.0.0:8000
============================================================

📡 MCP Protocol (Claude Desktop/Code):
   SSE endpoint: http://0.0.0.0:8000/sse

🌐 REST API (ChatGPT Custom GPTs):
   Tools list:   http://0.0.0.0:8000/api/tools
   Execute tool: http://0.0.0.0:8000/api/execute
   OpenAPI spec: http://0.0.0.0:8000/api/openapi.json

============================================================
```

### Test Locally

**For Claude Code:**
```json
{
  "mcp_servers": {
    "mcp-ke-local": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

**For ChatGPT:**
- Use `http://localhost:8000` as the server URL in Actions
- Note: ChatGPT may not be able to reach localhost, so this is mainly for testing the schema

---

## Deployment Commands

### Initial Deployment

```bash
# From mcp directory
fly deploy

# Follow prompts to create app
```

### Update Deployment

```bash
# After code changes
fly deploy

# Server automatically restarts with new code
```

### Monitor

```bash
# View logs
fly logs

# Check status
fly status

# Open dashboard
fly dashboard
```

### Environment Variables

Set if needed:
```bash
fly secrets set PUBLIC_URL=https://your-app.fly.dev
```

This URL is used in the OpenAPI schema generation.

---

## Cost

**Single Deployment:**
- One Fly.io app: ~$3-5/month
- Serves both Claude and ChatGPT
- Always-on, auto-scaling

**vs. Separate Deployments:**
- MCP-only server: $3-5/month
- REST-only server: $3-5/month
- Total: ~$6-10/month

**Savings: 50%** by using hybrid approach!

---

## Troubleshooting

### Claude Desktop URL Support

If you see "command is required" error when using URL:
- Current Claude Desktop beta may not fully support URL connections yet
- Use local stdio connection instead (works identically)
- URL support is being rolled out

### ChatGPT Can't Access Server

1. Check CORS is enabled (it is in hybrid_server.py)
2. Verify server is publicly accessible: `curl https://your-app.fly.dev/`
3. Make sure using `/api/` prefix for REST endpoints
4. Check OpenAPI schema is valid

### No Tools Showing

```bash
# Check tools are discovered
curl https://your-app.fly.dev/api/tools

# Should see all 23 tools listed
```

---

## Summary

**One Server, All Clients:**
- ✅ Deploy once to Fly.io
- ✅ Claude Desktop/Code use MCP protocol
- ✅ ChatGPT uses REST API
- ✅ Same tools, same data, same compute
- ✅ Half the cost of separate deployments

**URLs to Remember:**
- MCP: `https://your-app.fly.dev/sse`
- REST: `https://your-app.fly.dev/api/execute`
- OpenAPI: `https://your-app.fly.dev/api/openapi.json`
