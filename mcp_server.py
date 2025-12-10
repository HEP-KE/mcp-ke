import asyncio
import importlib
import inspect
import os
import pkgutil
import sys
from typing import Any

from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import Response
import uvicorn

# Import tools packages to discover all tools
import tools
import agent_tools


def log(msg: str):
    """Log to stderr to avoid breaking JSON-RPC on stdout."""
    print(msg, file=sys.stderr)

app = Server("mcp-ke")


def discover_tools() -> dict[str, callable]:
    """
    Auto-discover all @tool decorated functions from the tools and agent_tools packages.

    Returns:
        dict mapping tool names to their callable functions
    """
    discovered_tools = {}

    # Walk through all modules in both tools and agent_tools packages
    for package in [tools, agent_tools]:
        package_name = package.__name__
        for importer, modname, ispkg in pkgutil.walk_packages(
            path=package.__path__,
            prefix=f'{package_name}.',
            onerror=lambda x: None
        ):
            try:
                module = importlib.import_module(modname)

                # Find all callable objects in the module
                for name, obj in inspect.getmembers(module, callable):
                    # Check if it has the smolagents @tool decorator attributes
                    if hasattr(obj, '__wrapped__') or hasattr(obj, 'name'):
                        # Use the tool's name if available, otherwise use function name
                        tool_name = getattr(obj, 'name', name)
                        discovered_tools[tool_name] = obj

            except Exception as e:
                log(f"Warning: Could not import {modname}: {e}")
                continue

    return discovered_tools


def build_mcp_tool(name: str, func: callable) -> Tool:
    """
    Convert a smolagents @tool decorated function to an MCP Tool.

    Args:
        name: Tool name
        func: The tool function

    Returns:
        MCP Tool object
    """
    # For smolagents tools, inspect the actual 'forward' method instead of the wrapper
    actual_func = func
    if hasattr(func, 'forward'):
        actual_func = func.forward

    # Get function signature and docstring
    sig = inspect.signature(actual_func)
    doc = inspect.getdoc(func) or f"Tool: {name}"

    # Build JSON Schema for parameters
    properties = {}
    required = []

    for param_name, param in sig.parameters.items():
        if param_name in ('self', 'cls'):
            continue

        # Skip *args and **kwargs
        if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue

        # Basic type inference from annotations
        param_type = "string"  # default
        param_description = None

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
            elif annotation == object or annotation == 'object':
                # For numpy arrays or other objects, use array type
                param_type = "array"
            # Check for type hints
            elif hasattr(annotation, '__origin__'):
                origin = getattr(annotation, '__origin__', None)
                if origin == dict:
                    param_type = "object"
                elif origin in (list, tuple):
                    param_type = "array"

        param_schema = {"type": param_type}
        if param_description:
            param_schema["description"] = param_description

        properties[param_name] = param_schema

        # Mark as required if no default value
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


# Cache discovered tools
_TOOLS_CACHE = None


def get_tools() -> dict[str, callable]:
    """Get cached tools or discover them."""
    global _TOOLS_CACHE
    if _TOOLS_CACHE is None:
        _TOOLS_CACHE = discover_tools()
        log(f"Discovered {len(_TOOLS_CACHE)} tools: {list(_TOOLS_CACHE.keys())}")
    return _TOOLS_CACHE


@app.list_tools()
async def list_tools() -> list[Tool]:
    """Return all auto-discovered tools."""
    tools_dict = get_tools()
    return [build_mcp_tool(name, func) for name, func in tools_dict.items()]


@app.call_tool()
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

        # Unwrap args/kwargs if the MCP client wrapped them
        # Some MCP clients send {"args": [...], "kwargs": {...}}
        if isinstance(arguments, dict) and set(arguments.keys()) <= {"args", "kwargs"}:
            args = arguments.get("args", [])
            kwargs = arguments.get("kwargs", {})

            # Parse JSON strings if provided
            if isinstance(kwargs, str):
                try:
                    kwargs = json.loads(kwargs)
                except json.JSONDecodeError:
                    pass

            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except json.JSONDecodeError:
                    pass

            # Convert positional args to keyword args using the function signature
            if args and not kwargs:
                # Get the actual function to inspect
                actual_func = func.forward if hasattr(func, 'forward') else func
                sig = inspect.signature(actual_func)
                param_names = [
                    pname for pname, param in sig.parameters.items()
                    if pname not in ('self', 'cls')
                    and param.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
                ]

                # Map positional args to parameter names
                if isinstance(args, list) and param_names:
                    kwargs = dict(zip(param_names, args))
                elif not isinstance(args, list) and param_names:
                    # Single argument
                    kwargs = {param_names[0]: args}

            arguments = kwargs if kwargs else {}

        # Ensure arguments is a dict
        if not isinstance(arguments, dict):
            arguments = {}

        result = func(**arguments)

        # Convert result to string for MCP response
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


async def handle_sse(request):
    """Handle SSE connection requests."""
    async with SseServerTransport("/messages") as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


async def handle_messages(request):
    """Handle POST requests to /messages endpoint."""
    async with SseServerTransport("/messages") as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


async def main_stdio():
    """Start the MCP server with stdio transport (legacy mode)."""
    log("Starting MCP-KE server in STDIO mode...")
    log("Auto-discovering tools from tools/ and agent_tools/ directories...")

    # Trigger tool discovery
    get_tools()

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def main_sse():
    """Start the MCP server with SSE transport (HTTP mode)."""
    log("Starting MCP-KE server in SSE mode...")
    log("Auto-discovering tools from tools/ and agent_tools/ directories...")

    # Trigger tool discovery
    get_tools()

    # Get configuration from environment variables
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "8000"))

    # Create Starlette app with SSE transport
    sse_app = Starlette(
        routes=[
            Route("/sse", endpoint=handle_sse),
            Route("/messages", endpoint=handle_messages, methods=["POST"]),
        ]
    )

    log(f"Server listening on http://{host}:{port}")
    log(f"SSE endpoint: http://{host}:{port}/sse")
    log(f"Messages endpoint: http://{host}:{port}/messages")

    # Run the server
    uvicorn.run(sse_app, host=host, port=port)


if __name__ == "__main__":
    # Check if SSE mode is requested via environment variable
    mode = os.getenv("MCP_TRANSPORT", "stdio").lower()

    if mode == "sse":
        main_sse()
    else:
        asyncio.run(main_stdio())
