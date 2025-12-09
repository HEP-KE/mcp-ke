# ChatGPT Integration Guide

This guide explains how to use your MCP-KE tools with ChatGPT via a REST API wrapper.

## Why a REST Wrapper?

ChatGPT doesn't support the MCP (Model Context Protocol) directly. It uses:
- **OpenAPI/REST** for API interactions
- **Function calling** for tool execution

The REST wrapper (`rest_wrapper.py`) bridges this gap by:
1. Exposing MCP tools as REST endpoints
2. Auto-generating OpenAPI specifications
3. Providing CORS headers for ChatGPT access

---

## Option 1: Local Testing (Quick Start)

### 1. Install Additional Dependencies

```bash
pip install fastapi
```

### 2. Run the REST Wrapper Locally

```bash
python rest_wrapper.py
```

Output:
```
Starting REST API wrapper on http://0.0.0.0:8080
Available tools: 23
OpenAPI spec: http://0.0.0.0:8080/openapi.json
Interactive docs: http://0.0.0.0:8080/docs
```

### 3. Test the API

```bash
# List all tools
curl http://localhost:8080/tools

# Execute a tool
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "LCDM", "arguments": {}}'

# Get ΛCDM parameters directly
curl -X POST http://localhost:8080/tools/LCDM
```

### 4. View Interactive Documentation

Open in browser: http://localhost:8080/docs

This provides a Swagger UI to test all endpoints interactively.

---

## Option 2: Deploy to Fly.io (Production)

### 1. Create New Fly App for REST API

```bash
# In your mcp directory
fly apps create mcp-ke-rest-api
```

### 2. Deploy with REST Dockerfile

```bash
fly deploy --dockerfile Dockerfile.rest --app mcp-ke-rest-api
```

### 3. Get Your REST API URL

```bash
fly status --app mcp-ke-rest-api
```

Example URL: `https://mcp-ke-rest-api.fly.dev`

---

## Connecting to ChatGPT

### Option A: GPT Actions (ChatGPT Plus/Team/Enterprise)

1. **Create a Custom GPT**:
   - Go to https://chat.openai.com/gpts/editor
   - Click "Create a GPT"
   - Name it "Cosmology Analysis Assistant"

2. **Configure Actions**:
   - Click "Configure" → "Actions"
   - Click "Create new action"

3. **Import OpenAPI Schema**:
   - Enter your API URL: `https://your-rest-api.fly.dev/openapi.json`
   - Or paste the schema manually:

```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "MCP-KE REST API",
    "version": "1.0.0"
  },
  "servers": [
    {
      "url": "https://your-rest-api.fly.dev"
    }
  ],
  "paths": {
    "/tools/LCDM": {
      "post": {
        "summary": "Get ΛCDM cosmology parameters",
        "operationId": "getLCDM",
        "responses": {
          "200": {
            "description": "ΛCDM parameters",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object"
                }
              }
            }
          }
        }
      }
    },
    "/tools/compute_power_spectrum": {
      "post": {
        "summary": "Compute matter power spectrum",
        "operationId": "computePowerSpectrum",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "h": {"type": "number"},
                  "Omega_b": {"type": "number"},
                  "Omega_cdm": {"type": "number"},
                  "k_values": {
                    "type": "array",
                    "items": {"type": "number"}
                  }
                },
                "required": ["h", "Omega_b", "Omega_cdm", "k_values"]
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Power spectrum values"
          }
        }
      }
    }
  }
}
```

4. **Test the Action**:
   - Click "Test" in the Actions panel
   - Try: "Get ΛCDM parameters"

5. **Save and Use**:
   - Save your Custom GPT
   - Use it in chat: "What are the ΛCDM cosmology parameters?"

### Option B: Zapier AI Actions (Alternative)

If you have Zapier access:

1. Create a Zapier Action that calls your REST API
2. Connect it to ChatGPT via Zapier's ChatGPT integration
3. More complex but doesn't require ChatGPT Plus

---

## Available REST Endpoints

### List Tools
```
GET /tools
```

Returns all 23 available tools with parameters.

### Execute Generic Tool
```
POST /execute
Body: {
  "tool_name": "LCDM",
  "arguments": {}
}
```

### Specific Tool Endpoints

These provide cleaner OpenAPI specs for ChatGPT:

- `POST /tools/LCDM` - Get ΛCDM parameters
- `POST /tools/nu_mass` - Get neutrino mass parameters
- `POST /tools/wCDM` - Get wCDM parameters
- `POST /tools/load_observational_data` - Load eBOSS data
- `POST /tools/compute_power_spectrum` - Compute P(k)

---

## Security Considerations

### Current Setup
- **No authentication** - REST API is publicly accessible
- **CORS enabled** for ChatGPT domains
- Fine for personal use/testing

### Adding Authentication

For production use, add API key authentication:

```python
# In rest_wrapper.py, add:
from fastapi import Header, HTTPException

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API key")

# Add to endpoints:
@app.post("/execute", dependencies=[Depends(verify_api_key)])
async def execute_tool(request: ToolRequest):
    ...
```

Then set environment variable on Fly.io:
```bash
fly secrets set API_KEY=your-secret-key --app mcp-ke-rest-api
```

In ChatGPT Custom GPT actions, add header:
```
X-API-Key: your-secret-key
```

---

## Limitations vs Native MCP

### REST Wrapper
- ✅ Works with ChatGPT
- ✅ Standard HTTP/REST
- ❌ Less efficient (HTTP overhead)
- ❌ No streaming responses
- ❌ Requires separate deployment

### Native MCP (Claude Desktop/Code)
- ✅ Efficient streaming protocol
- ✅ Native tool integration
- ✅ Better error handling
- ❌ Only works with MCP-compatible clients

---

## Troubleshooting

### CORS Errors in ChatGPT

If you see CORS errors:

```python
# Update rest_wrapper.py CORS settings:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all (less secure)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Tool Not Found

Check available tools:
```bash
curl https://your-rest-api.fly.dev/tools
```

### Deployment Issues

```bash
# Check logs
fly logs --app mcp-ke-rest-api

# Check status
fly status --app mcp-ke-rest-api
```

---

## Cost Considerations

Running both MCP and REST APIs:
- **MCP Server** (sse branch): $3-5/month
- **REST Wrapper**: $3-5/month
- **Total**: ~$6-10/month

Alternatively, run only REST wrapper if you only need ChatGPT:
- Deploy just REST wrapper
- Total: ~$3-5/month

---

## Summary

**For ChatGPT**:
1. Deploy REST wrapper to Fly.io
2. Create Custom GPT with OpenAPI actions
3. Use tools via natural language

**For Claude**:
- Use native MCP (already configured)
- Better performance and experience

Both can run simultaneously on Fly.io!
