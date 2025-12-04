# MCP-KE Deployment Guide

This guide covers deploying MCP-KE server with SSE (Server-Sent Events) transport for remote access.

## Table of Contents

- [Overview](#overview)
- [SSE vs STDIO Transport](#sse-vs-stdio-transport)
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Cloud Platform Deployments](#cloud-platform-deployments)
  - [Railway](#railway)
  - [Render](#render)
  - [Fly.io](#flyio)
- [Client Configuration](#client-configuration)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)

---

## Overview

The `sse` branch converts MCP-KE from stdio-based (local process) to SSE-based (HTTP server) transport. This enables:

- **Remote access**: Users connect to a centralized server via URL
- **No local installation**: Users don't need to install CLASS or Python dependencies
- **Centralized data**: Observational data and models hosted in one place
- **Scalable deployment**: Run on cloud platforms with auto-scaling

**Architecture:**
```
┌─────────────────┐          HTTP/SSE          ┌──────────────────┐
│  MCP Client     │ ───────────────────────────▶│   MCP-KE Server  │
│ (Claude Desktop │         (Port 8000)         │   (Docker/Cloud) │
│  Claude Code)   │                             │                  │
└─────────────────┘          /sse endpoint      └──────────────────┘
                             /messages endpoint
```

---

## SSE vs STDIO Transport

### STDIO (Default - `main` branch)
- **Communication**: stdin/stdout pipes
- **Execution**: Client spawns local Python process
- **Use case**: Local development, single-user
- **Pros**: Fast, no network overhead, full data privacy
- **Cons**: Every user needs full installation (CLASS, Python deps)

### SSE (SSE branch - this deployment)
- **Communication**: HTTP with Server-Sent Events
- **Execution**: Client connects to remote HTTP server
- **Use case**: Multi-user, remote deployment
- **Pros**: No client-side installation, centralized compute/data
- **Cons**: Network latency, server hosting costs

### Switching Between Modes

```bash
# Run in STDIO mode (default - backward compatible)
python mcp_server.py

# Run in SSE mode
MCP_TRANSPORT=sse python mcp_server.py

# Or set in environment
export MCP_TRANSPORT=sse
python mcp_server.py
```

---

## Local Development

### Prerequisites
- Python 3.8+
- Docker (optional, recommended)

### Quick Start with Docker Compose

```bash
# Build and start the server
docker-compose up --build

# Server will be available at:
# - SSE endpoint: http://localhost:8000/sse
# - Messages endpoint: http://localhost:8000/messages

# Stop the server
docker-compose down
```

### Manual Setup (without Docker)

```bash
# Install dependencies
pip install -e .

# Start server in SSE mode
MCP_TRANSPORT=sse MCP_PORT=8000 python mcp_server.py
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_TRANSPORT` | `stdio` | Transport mode: `stdio` or `sse` |
| `MCP_HOST` | `0.0.0.0` | Server bind address (SSE mode only) |
| `MCP_PORT` | `8000` | Server port (SSE mode only) |
| `PYTHONUNBUFFERED` | `1` | Disable Python output buffering |

---

## Docker Deployment

### Build Image

```bash
docker build -t mcp-ke:latest .
```

### Run Container

```bash
docker run -d \
  --name mcp-ke-server \
  -p 8000:8000 \
  -e MCP_TRANSPORT=sse \
  -v $(pwd)/input:/app/input:ro \
  -v $(pwd)/out:/app/out \
  mcp-ke:latest
```

### Volume Mounts

- `/app/input`: Mount observational data files (read-only)
- `/app/out`: Mount output directory for plots/results (read-write)

### Data Management

**Option 1: Bundle data in image**
- Place data files in `input/` directory before building
- Data is baked into the Docker image
- Pros: Simple, self-contained
- Cons: Large image, data updates require rebuild

**Option 2: Mount data at runtime** (recommended)
```bash
docker run -v /path/to/your/data:/app/input:ro mcp-ke:latest
```
- Data stays outside container
- Pros: Smaller image, easy updates
- Cons: Requires volume management

---

## Cloud Platform Deployments

### Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template)

**Manual Deployment:**

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   railway login
   ```

2. **Initialize project:**
   ```bash
   railway init
   ```

3. **Deploy:**
   ```bash
   railway up
   ```

4. **Get deployment URL:**
   ```bash
   railway domain
   # Example output: mcp-ke-server.railway.app
   ```

**Configuration:**
- Railway auto-detects `Dockerfile`
- Configuration in `railway.json`
- Environment variables set via Railway dashboard or CLI
- Cost: ~$5/month (Starter plan)

---

### Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

**Manual Deployment:**

1. **Create account:** https://render.com

2. **Create new Web Service:**
   - Connect your GitHub repository
   - Select `sse` branch
   - Render auto-detects `Dockerfile`

3. **Configure:**
   - Name: `mcp-ke-server`
   - Region: Choose closest to your users
   - Instance Type: Starter ($7/month) or Free (with limitations)
   - Environment variables (auto-loaded from `render.yaml`):
     - `MCP_TRANSPORT=sse`
     - `MCP_HOST=0.0.0.0`
     - `MCP_PORT=8000`

4. **Deploy:**
   - Click "Create Web Service"
   - Render builds and deploys automatically

5. **Get URL:**
   - Format: `https://mcp-ke-server.onrender.com`

**Configuration:**
- Configuration in `render.yaml`
- Auto-deploy on git push (configurable)
- Free tier: sleeps after 15 min inactivity, cold start ~30s
- Paid tier: Always on, no cold starts
- Cost: Free tier available, paid from $7/month

---

### Fly.io

**Manual Deployment:**

1. **Install Fly CLI:**
   ```bash
   curl -L https://fly.io/install.sh | sh
   fly auth login
   ```

2. **Launch app:**
   ```bash
   fly launch
   # Follow prompts:
   # - App name: mcp-ke-server
   # - Region: Choose closest to users
   # - Don't deploy yet: N
   ```

3. **Configure app (edit `fly.toml` if needed):**
   - Already created with sensible defaults
   - Adjust `primary_region`, `memory_mb`, `cpus` as needed

4. **Deploy:**
   ```bash
   fly deploy
   ```

5. **Get URL:**
   ```bash
   fly status
   # Example: https://mcp-ke-server.fly.dev
   ```

6. **Scale (optional):**
   ```bash
   # Increase memory for CLASS computations
   fly scale memory 2048

   # Add more instances
   fly scale count 2
   ```

**Configuration:**
- Configuration in `fly.toml`
- Auto-scaling: Machines sleep when idle, wake on request
- Persistent volumes: Add if you need persistent data
- Cost: ~$3-5/month (shared-cpu-1x with 1GB RAM)

**Data Management on Fly.io:**

If you need persistent data storage:

```bash
# Create volume for input data
fly volumes create mcp_data --size 1

# Update fly.toml to mount volume
# Add under [mounts]:
[mounts]
  source = "mcp_data"
  destination = "/app/input"
```

---

## Client Configuration

### Claude Desktop

Edit your Claude Desktop configuration (`claude_desktop_config.json`):

**For local Docker:**
```json
{
  "mcpServers": {
    "mcp-ke": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

**For cloud deployment:**
```json
{
  "mcpServers": {
    "mcp-ke": {
      "url": "https://your-deployment-url.com/sse"
    }
  }
}
```

### Claude Code

Edit `.claude/settings.json`:

```json
{
  "mcp_servers": {
    "mcp-ke": {
      "url": "https://your-deployment-url.com/sse"
    }
  }
}
```

### Custom MCP Clients

Connect to SSE endpoint:
- **SSE Stream**: `GET https://your-server.com/sse`
- **Messages**: `POST https://your-server.com/messages`

---

## Security Considerations

### Current Implementation

The SSE server currently has **NO AUTHENTICATION**. It's designed for:
- Personal deployments
- Trusted networks
- Development/testing

### Adding Authentication

For production deployments, add authentication:

**Option 1: API Key Middleware**

```python
# In mcp_server.py, add middleware:
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        api_key = request.headers.get("X-API-Key")
        if api_key != os.getenv("MCP_API_KEY"):
            return Response("Unauthorized", status_code=401)
        return await call_next(request)

# Add to Starlette app:
sse_app.add_middleware(APIKeyMiddleware)
```

**Option 2: Platform-Level Protection**
- Fly.io: Use Fly private networks
- Railway/Render: Use environment variables for URL obfuscation
- Add reverse proxy with HTTP Basic Auth (nginx, Caddy)

**Option 3: Network Restrictions**
- Deploy to private VPC
- Use Tailscale/Wireguard for access control
- Firewall rules to restrict IP ranges

### Data Privacy

**Agent Tools (arXiv, power spectrum):**
- Require user-provided LLM API keys (passed as tool parameters)
- Server doesn't store API keys
- Users control their LLM costs

**Observational Data:**
- Public eBOSS data - no privacy concerns
- If using proprietary data, ensure proper access controls

---

## Troubleshooting

### Server Won't Start

**Issue:** Server fails to start in SSE mode

```bash
# Check logs
docker logs mcp-ke-server

# Common issues:
# 1. Port already in use
lsof -i :8000  # Find conflicting process
MCP_PORT=8001 python mcp_server.py  # Use different port

# 2. Missing dependencies
pip install starlette uvicorn
```

### Client Can't Connect

**Issue:** Client fails to connect to SSE endpoint

**Check server accessibility:**
```bash
# Test locally
curl http://localhost:8000/sse

# Test remotely
curl https://your-deployment-url.com/sse
```

**Common issues:**
1. **Firewall blocking port 8000**: Check cloud platform firewall rules
2. **Wrong URL in client config**: Ensure `/sse` endpoint suffix
3. **Server not running**: Check `docker ps` or cloud platform logs

### Tool Execution Errors

**Issue:** Tools fail with CLASS-related errors

**Solution:**
- CLASS compilation failed during Docker build
- Check Docker build logs: `docker build -t mcp-ke:latest . --no-cache`
- Ensure build dependencies installed (see Dockerfile)

**Issue:** Input data not found

**Solution:**
```bash
# Check if data mounted correctly
docker exec mcp-ke-server ls -la /app/input

# Verify volume mount in docker-compose.yml or docker run command
```

### Performance Issues

**Issue:** Slow CLASS computations

**Solutions:**
1. **Increase memory** (CLASS is memory-intensive):
   ```bash
   # Fly.io
   fly scale memory 2048

   # Docker
   docker run --memory=2g mcp-ke:latest
   ```

2. **Optimize CLASS parameters** in cosmology models
3. **Cache results** using save/load tools

**Issue:** Cold start latency (Render free tier, Fly.io auto-scaling)

**Solutions:**
- Upgrade to paid tier (always-on instances)
- Accept cold start delay (~30-60s)
- Use health check endpoint to pre-warm: `curl /sse`

---

## Cost Comparison

| Platform | Free Tier | Paid Tier | Notes |
|----------|-----------|-----------|-------|
| **Railway** | $5 credit | ~$5-10/month | Easy setup, great DX |
| **Render** | 750 hrs/month | ~$7-25/month | Free tier sleeps after 15min |
| **Fly.io** | Generous free tier | ~$3-5/month | Best value, more config |
| **Local Docker** | Free | Infrastructure costs | Best for personal use |

**Recommendation:**
- **Development**: Local Docker
- **Personal/small team**: Fly.io (best cost/performance)
- **Production/team**: Railway or Render (easier management)

---

## Next Steps

1. **Deploy to platform of choice** (see sections above)
2. **Configure client** with deployment URL
3. **Test tools** using Claude Desktop/Code
4. **Monitor usage** via platform dashboards
5. **Add authentication** if exposing publicly
6. **Optimize costs** by adjusting instance size/scaling

For issues or questions, see main [README.md](../README.md) or open a GitHub issue.
