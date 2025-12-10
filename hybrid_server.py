"""
Hybrid server that supports both MCP (for Claude) and REST (for ChatGPT).

This single server deployment can be used by:
- Claude Desktop: via MCP SSE protocol at /sse
- ChatGPT: via REST API at /api/*
"""

import asyncio
import importlib
import inspect
import os
import pkgutil
from typing import Any, Dict

from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse, Response
from starlette.middleware.cors import CORSMiddleware
import uvicorn

# Import tools packages
import tools
import agent_tools

# Create MCP server
mcp_app = Server("mcp-ke")


def discover_tools() -> dict[str, callable]:
    """Auto-discover all @tool decorated functions."""
    discovered_tools = {}

    for package in [tools, agent_tools]:
        package_name = package.__name__
        for importer, modname, ispkg in pkgutil.walk_packages(
            path=package.__path__,
            prefix=f'{package_name}.',
            onerror=lambda x: None
        ):
            try:
                module = importlib.import_module(modname)
                for name, obj in inspect.getmembers(module, callable):
                    if hasattr(obj, '__wrapped__') or hasattr(obj, 'name'):
                        tool_name = getattr(obj, 'name', name)
                        discovered_tools[tool_name] = obj
            except Exception as e:
                print(f"Warning: Could not import {modname}: {e}")
                continue

    return discovered_tools


def build_mcp_tool(name: str, func: callable) -> Tool:
    """Convert a tool function to an MCP Tool."""
    sig = inspect.signature(func)
    doc = inspect.getdoc(func) or f"Tool: {name}"

    properties = {}
    required = []

    for param_name, param in sig.parameters.items():
        if param_name in ('self', 'cls'):
            continue

        param_type = "string"
        if param.annotation != inspect.Parameter.empty:
            annotation = param.annotation
            if annotation in (int, 'int'):
                param_type = "integer"
            elif annotation in (float, 'float'):
                param_type = "number"
            elif annotation in (bool, 'bool'):
                param_type = "boolean"
            elif annotation in (dict, 'dict'):
                param_type = "object"

        properties[param_name] = {"type": param_type}

        if param.default == inspect.Parameter.empty:
            required.append(param_name)

    return Tool(
        name=name,
        description=doc,
        inputSchema={
            "type": "object",
            "properties": properties,
            "required": required
        }
    )


# Cache tools
_TOOLS_CACHE = None


def get_tools() -> dict[str, callable]:
    """Get cached tools or discover them."""
    global _TOOLS_CACHE
    if _TOOLS_CACHE is None:
        _TOOLS_CACHE = discover_tools()
        print(f"Discovered {len(_TOOLS_CACHE)} tools: {list(_TOOLS_CACHE.keys())}")
    return _TOOLS_CACHE


# MCP Protocol Handlers (for Claude Desktop/Code)
@mcp_app.list_tools()
async def list_tools() -> list[Tool]:
    """Return all auto-discovered tools."""
    tools_dict = get_tools()
    return [build_mcp_tool(name, func) for name, func in tools_dict.items()]


@mcp_app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute a tool and return its response."""
    tools_dict = get_tools()

    if name not in tools_dict:
        return [TextContent(
            type="text",
            text=f"Error: Tool '{name}' not found. Available tools: {list(tools_dict.keys())}"
        )]

    try:
        import json

        func = tools_dict[name]

        # Debug logging
        print(f"[DEBUG] Tool: {name}")
        print(f"[DEBUG] Raw arguments: {arguments}")
        print(f"[DEBUG] Arguments type: {type(arguments)}")

        # Unwrap args/kwargs if the MCP client wrapped them
        # Some MCP clients send {"args": [...], "kwargs": {...}}
        # but smolagents tools expect direct parameters
        if isinstance(arguments, dict) and set(arguments.keys()) <= {"args", "kwargs"}:
            # If we have both args and kwargs, we need to handle positional args
            args = arguments.get("args", [])
            kwargs = arguments.get("kwargs", {})

            # Parse JSON strings if provided
            if isinstance(kwargs, str):
                try:
                    kwargs = json.loads(kwargs)
                except json.JSONDecodeError:
                    # If it's not valid JSON, treat it as a string parameter
                    pass

            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except json.JSONDecodeError:
                    # If it's not valid JSON, keep it as string
                    pass

            # Merge kwargs with converted positional args
            if args and not kwargs:
                # For smolagents tools, we can't reliably convert positional to keyword args
                # because they're wrapped with (*args, **kwargs) signatures.
                # Instead, just pass the args as-is by converting to the inner function's actual params

                # Check if this is a smolagents tool (has 'forward' method)
                if hasattr(func, 'forward'):
                    # Get the actual tool function's signature
                    actual_func = getattr(func, 'forward', func)
                    sig = inspect.signature(actual_func)
                    param_names = [
                        name for name, param in sig.parameters.items()
                        if name not in ('self', 'cls')
                        and param.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
                    ]
                else:
                    sig = inspect.signature(func)
                    param_names = [
                        name for name, param in sig.parameters.items()
                        if name not in ('self', 'cls')
                        and param.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
                    ]

                if isinstance(args, list):
                    # List of positional arguments
                    if len(args) > 0 and len(param_names) > 0:
                        kwargs = dict(zip(param_names, args))
                elif isinstance(args, str) and len(param_names) > 0:
                    # Single string argument - assign to first parameter
                    kwargs = {param_names[0]: args}
            elif args and kwargs:
                # If we have both, prefer kwargs but warn
                pass

            arguments = kwargs if kwargs else {}

        # Debug final arguments
        print(f"[DEBUG] Final arguments to pass: {arguments}")
        print(f"[DEBUG] Function signature: {inspect.signature(func)}")

        result = func(**arguments)
        result_str = str(result)
        return [TextContent(type="text", text=result_str)]

    except TypeError as e:
        import traceback
        # Check if this is a missing argument error
        if "missing" in str(e) and "required" in str(e):
            sig = inspect.signature(func)
            param_info = []
            for param_name, param in sig.parameters.items():
                if param_name not in ('self', 'cls'):
                    required = param.default == inspect.Parameter.empty
                    param_info.append(f"  - {param_name}: {param.annotation} {'(required)' if required else f'(optional, default={param.default})'}")

            param_list = "\n".join(param_info)
            error_msg = f"Error: Tool '{name}' is missing required arguments.\n\nExpected parameters:\n{param_list}\n\nReceived arguments: {arguments}\n\nOriginal error: {str(e)}"
            return [TextContent(type="text", text=error_msg)]
        else:
            error_msg = f"Error executing tool '{name}': {str(e)}\n{traceback.format_exc()}"
            return [TextContent(type="text", text=error_msg)]

    except Exception as e:
        import traceback
        error_msg = f"Error executing tool '{name}': {str(e)}\n{traceback.format_exc()}"
        return [TextContent(type="text", text=error_msg)]


# REST API Handlers (for ChatGPT)
async def rest_root(request):
    """REST API root endpoint."""
    return JSONResponse({
        "name": "MCP-KE Hybrid Server",
        "version": "1.0.0",
        "protocols": {
            "mcp": {
                "description": "Model Context Protocol (for Claude Desktop/Code)",
                "endpoints": {
                    "sse": "/sse",
                    "messages": "/messages"
                }
            },
            "rest": {
                "description": "REST API (for ChatGPT Custom GPTs)",
                "endpoints": {
                    "tools": "/api/tools",
                    "execute": "/api/execute",
                    "openapi": "/api/openapi.json"
                }
            }
        },
        "tools_count": len(get_tools())
    })


async def rest_list_tools(request):
    """REST: List all tools."""
    tools_dict = get_tools()
    tool_list = []

    for name, func in tools_dict.items():
        sig = inspect.signature(func)
        doc = inspect.getdoc(func) or f"Tool: {name}"

        params = {}
        for param_name, param in sig.parameters.items():
            if param_name in ('self', 'cls'):
                continue
            params[param_name] = {
                "required": param.default == inspect.Parameter.empty,
                "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "string"
            }

        tool_list.append({
            "name": name,
            "description": doc,
            "parameters": params
        })

    return JSONResponse({"tools": tool_list})


async def rest_execute_tool(request):
    """REST: Execute a tool."""
    try:
        body = await request.json()
        tool_name = body.get("tool_name")
        arguments = body.get("arguments", {})

        if tool_name not in get_tools():
            return JSONResponse(
                {"success": False, "error": f"Tool '{tool_name}' not found"},
                status_code=404
            )

        func = get_tools()[tool_name]
        result = func(**arguments)

        return JSONResponse({
            "success": True,
            "result": str(result)
        })

    except Exception as e:
        import traceback
        return JSONResponse({
            "success": False,
            "error": f"{str(e)}\n{traceback.format_exc()}"
        }, status_code=500)


async def rest_openapi(request):
    """REST: OpenAPI schema for ChatGPT."""
    return JSONResponse({
        "openapi": "3.1.0",
        "info": {
            "title": "MCP-KE API",
            "description": "Cosmology analysis tools",
            "version": "1.0.0"
        },
        "servers": [
            {"url": os.getenv("PUBLIC_URL", "http://localhost:8000")}
        ],
        "paths": {
            "/api/tools": {
                "get": {
                    "summary": "List available tools",
                    "operationId": "listTools",
                    "responses": {
                        "200": {"description": "List of tools"}
                    }
                }
            },
            "/api/execute": {
                "post": {
                    "summary": "Execute a tool",
                    "operationId": "executeTool",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "tool_name": {"type": "string"},
                                        "arguments": {"type": "object"}
                                    },
                                    "required": ["tool_name"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "Tool execution result"}
                    }
                }
            }
        }
    })


# MCP SSE Handlers
async def handle_sse(request):
    """Handle MCP SSE connection."""
    async with SseServerTransport("/messages") as (read_stream, write_stream):
        await mcp_app.run(read_stream, write_stream, mcp_app.create_initialization_options())


async def handle_messages(request):
    """Handle MCP POST messages."""
    async with SseServerTransport("/messages") as (read_stream, write_stream):
        await mcp_app.run(read_stream, write_stream, mcp_app.create_initialization_options())


def main():
    """Start the hybrid server."""
    print("Starting MCP-KE Hybrid Server...")
    print("Auto-discovering tools...")
    get_tools()

    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "8000"))

    # Create Starlette app with both MCP and REST routes
    app = Starlette(
        routes=[
            # Root
            Route("/", endpoint=rest_root),

            # MCP endpoints (for Claude)
            Route("/sse", endpoint=handle_sse),
            Route("/messages", endpoint=handle_messages, methods=["POST"]),

            # REST API endpoints (for ChatGPT)
            Route("/api/tools", endpoint=rest_list_tools),
            Route("/api/execute", endpoint=rest_execute_tool, methods=["POST"]),
            Route("/api/openapi.json", endpoint=rest_openapi),
        ]
    )

    # Add CORS for ChatGPT
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://chat.openai.com", "https://chatgpt.com", "*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    print(f"\n{'='*60}")
    print(f"Server listening on http://{host}:{port}")
    print(f"{'='*60}")
    print(f"\n📡 MCP Protocol (Claude Desktop/Code):")
    print(f"   SSE endpoint: http://{host}:{port}/sse")
    print(f"\n🌐 REST API (ChatGPT Custom GPTs):")
    print(f"   Tools list:   http://{host}:{port}/api/tools")
    print(f"   Execute tool: http://{host}:{port}/api/execute")
    print(f"   OpenAPI spec: http://{host}:{port}/api/openapi.json")
    print(f"\n{'='*60}\n")

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
