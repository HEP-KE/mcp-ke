"""
REST API wrapper for MCP-KE server to enable ChatGPT integration.

This creates a FastAPI server that wraps MCP tools as REST endpoints,
making them compatible with ChatGPT's function calling.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, Optional
import uvicorn

# Import your tools directly
import tools
import agent_tools
from mcp_server import discover_tools

app = FastAPI(
    title="MCP-KE REST API",
    description="REST wrapper for MCP-KE cosmology analysis tools",
    version="1.0.0"
)

# Enable CORS for ChatGPT to access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chat.openai.com", "https://chatgpt.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Discover all tools
TOOLS = discover_tools()


class ToolRequest(BaseModel):
    """Request model for tool execution."""
    tool_name: str
    arguments: Dict[str, Any]


class ToolResponse(BaseModel):
    """Response model for tool execution."""
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "MCP-KE REST API",
        "version": "1.0.0",
        "tools_count": len(TOOLS),
        "endpoints": {
            "list_tools": "/tools",
            "execute_tool": "/execute",
            "openapi_spec": "/openapi.json"
        }
    }


@app.get("/tools")
async def list_tools():
    """List all available tools with their metadata."""
    tool_list = []

    for name, func in TOOLS.items():
        import inspect
        sig = inspect.signature(func)
        doc = inspect.getdoc(func) or f"Tool: {name}"

        # Build parameter info
        params = {}
        for param_name, param in sig.parameters.items():
            if param_name in ('self', 'cls'):
                continue

            param_info = {
                "required": param.default == inspect.Parameter.empty,
                "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "string"
            }
            params[param_name] = param_info

        tool_list.append({
            "name": name,
            "description": doc,
            "parameters": params
        })

    return {"tools": tool_list}


@app.post("/execute", response_model=ToolResponse)
async def execute_tool(request: ToolRequest):
    """Execute a tool with given arguments."""
    tool_name = request.tool_name

    if tool_name not in TOOLS:
        raise HTTPException(
            status_code=404,
            detail=f"Tool '{tool_name}' not found. Available: {list(TOOLS.keys())}"
        )

    try:
        func = TOOLS[tool_name]
        result = func(**request.arguments)

        return ToolResponse(
            success=True,
            result=str(result)
        )

    except Exception as e:
        import traceback
        return ToolResponse(
            success=False,
            error=f"{str(e)}\n{traceback.format_exc()}"
        )


# Individual tool endpoints for ChatGPT function calling
# These provide cleaner OpenAPI specs

@app.post("/tools/LCDM")
async def tool_LCDM():
    """Get ΛCDM cosmology parameters."""
    try:
        result = TOOLS["LCDM"]()
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/nu_mass")
async def tool_nu_mass():
    """Get neutrino mass cosmology parameters."""
    try:
        result = TOOLS["nu_mass"]()
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/wCDM")
async def tool_wCDM():
    """Get wCDM dark energy cosmology parameters."""
    try:
        result = TOOLS["wCDM"]()
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/load_observational_data")
async def tool_load_observational_data(filename: str = "DR14_pm3d_19kbins.txt"):
    """Load eBOSS observational data."""
    try:
        result = TOOLS["load_observational_data"](filename=filename)
        return {"success": True, "result": str(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/compute_power_spectrum")
async def tool_compute_power_spectrum(
    h: float,
    Omega_b: float,
    Omega_cdm: float,
    k_values: list
):
    """Compute matter power spectrum P(k) using CLASS."""
    try:
        result = TOOLS["compute_power_spectrum"](
            h=h, Omega_b=Omega_b, Omega_cdm=Omega_cdm, k_values=k_values
        )
        return {"success": True, "result": result.tolist() if hasattr(result, 'tolist') else result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import os
    host = os.getenv("REST_HOST", "0.0.0.0")
    port = int(os.getenv("REST_PORT", "8080"))

    print(f"Starting REST API wrapper on http://{host}:{port}")
    print(f"Available tools: {len(TOOLS)}")
    print(f"OpenAPI spec: http://{host}:{port}/openapi.json")
    print(f"Interactive docs: http://{host}:{port}/docs")

    uvicorn.run(app, host=host, port=port)
