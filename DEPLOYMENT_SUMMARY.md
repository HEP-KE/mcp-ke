# Deployment Summary - Quick Reference

## ✅ What You Have Now

A **single hybrid server** on Fly.io that works with both Claude and ChatGPT:

**URL:** `https://mcp-ke-server-holy-tree-8438.fly.dev`

---

## 🎯 How to Connect Each Client

### Claude Desktop
**Current Status:** The UI shows URL support, but it may still require local stdio connections.

**Option 1: Local (Recommended for now)**
Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "mcp-ke": {
      "command": "/Users/nesar/Projects/HEP/AmSC_HEP/.conda/bin/python",
      "args": [
        "/Users/nesar/Projects/HEP/AmSC_HEP/hep-ke/mcp/mcp_server.py"
      ]
    }
  }
}
```

**Option 2: Remote (If URL support works)**
Try this in Claude Desktop's "New App" interface:
- Name: `mcp-ke-remote`
- URL: `https://mcp-ke-server-holy-tree-8438.fly.dev/sse`
- Auth: No Auth

If you get "command is required" error, use Option 1 instead.

---

### Claude Code

Edit `.claude/settings.json`:
```json
{
  "mcp_servers": {
    "mcp-ke": {
      "url": "https://mcp-ke-server-holy-tree-8438.fly.dev/sse"
    }
  }
}
```

This should work! Claude Code has better URL support than Desktop currently.

---

### ChatGPT

**Important:** ChatGPT does NOT use MCP protocol. It uses REST API via Custom GPT Actions.

**Steps:**
1. Go to https://chat.openai.com/gpts/editor
2. Create a Custom GPT named "Cosmology Assistant"
3. Click "Configure" → "Actions" → "Create new action"
4. Use this OpenAPI URL:
   ```
   https://mcp-ke-server-holy-tree-8438.fly.dev/api/openapi.json
   ```
5. Or import schema manually from the URL above
6. Save and test!

**Key Difference:**
- **Claude:** Uses `/sse` endpoint (MCP protocol)
- **ChatGPT:** Uses `/api/execute` endpoint (REST API)
- **Same server serves both!**

---

## 🔄 Update Your Deployment

### Redeploy with Hybrid Server

```bash
# From mcp directory
fly deploy
```

This will deploy the new `hybrid_server.py` which supports both protocols.

**After deployment, both will work:**
- Claude → `https://mcp-ke-server-holy-tree-8438.fly.dev/sse`
- ChatGPT → `https://mcp-ke-server-holy-tree-8438.fly.dev/api/execute`

---

## 🧪 Test Your Setup

### Test MCP Endpoint (for Claude)
```bash
curl https://mcp-ke-server-holy-tree-8438.fly.dev/sse
# Should see SSE headers
```

### Test REST API (for ChatGPT)
```bash
# List tools
curl https://mcp-ke-server-holy-tree-8438.fly.dev/api/tools

# Execute tool
curl -X POST https://mcp-ke-server-holy-tree-8438.fly.dev/api/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "LCDM", "arguments": {}}'
```

### Test in Browser
Visit: https://mcp-ke-server-holy-tree-8438.fly.dev/

Should show server info with both protocol endpoints.

---

## 📊 Architecture

```
                    Fly.io Hybrid Server
                 (mcp-ke-server-holy-tree-8438)
                              │
                ┌─────────────┴─────────────┐
                │                           │
         /sse (MCP Protocol)         /api/* (REST API)
                │                           │
         ┌──────┴──────┐            ┌───────┴────────┐
         │  Claude     │            │   ChatGPT      │
         │  Desktop    │            │   Custom GPT   │
         │  Claude     │            │   Actions      │
         │  Code       │            │                │
         └─────────────┘            └────────────────┘
```

**One server, two protocols, all clients supported!**

---

## 💰 Cost

**Before:** $6-10/month (separate MCP + REST servers)
**After:** $3-5/month (single hybrid server)
**Savings:** 50%

---

## 📖 Full Documentation

- **Quick Start:** This file
- **Unified Deployment:** [07_UNIFIED_DEPLOYMENT.md](documentation/07_UNIFIED_DEPLOYMENT.md)
- **SSE/Docker Setup:** [05_DEPLOYMENT.md](documentation/05_DEPLOYMENT.md)
- **ChatGPT Details:** [06_CHATGPT_INTEGRATION.md](documentation/06_CHATGPT_INTEGRATION.md)
- **Architecture:** [02_ARCHITECTURE.md](documentation/02_ARCHITECTURE.md)

---

## ❓ Common Issues

### "command is required" in Claude Desktop
- URL support may not be fully available yet
- Use local stdio connection instead
- Works identically, just spawns process locally

### ChatGPT can't find server
- Make sure using `/api/` prefix
- Use `https://mcp-ke-server-holy-tree-8438.fly.dev` as server URL in OpenAPI
- Check CORS is enabled (it is in hybrid_server.py)

### Tools not showing
```bash
# Check server is running
fly status

# Check tools are discovered
curl https://mcp-ke-server-holy-tree-8438.fly.dev/api/tools
```

---

## ✨ Next Steps

1. **Redeploy:** Run `fly deploy` to activate hybrid server
2. **Test Claude Code:** Try the URL config
3. **Create ChatGPT Custom GPT:** Follow steps above
4. **Keep Claude Desktop local:** Until URL support is stable

All your tools will work across all clients!
