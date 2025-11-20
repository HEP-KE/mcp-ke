import asyncio
import importlib
import inspect
import pkgutil
from typing import Any

from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio

# Import tools packages to discover all tools
import tools
import agent_tools

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
                print(f"Warning: Could not import {modname}: {e}")
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
    # Get function signature and docstring
    sig = inspect.signature(func)
    doc = inspect.getdoc(func) or f"Tool: {name}"

    # Build JSON Schema for parameters
    properties = {}
    required = []

    for param_name, param in sig.parameters.items():
        if param_name in ('self', 'cls'):
            continue

        # Basic type inference from annotations
        param_type = "string"  # default
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
        print(f"Discovered {len(_TOOLS_CACHE)} tools: {list(_TOOLS_CACHE.keys())}")
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
        func = tools_dict[name]
        result = func(**arguments)

        # Convert result to string for MCP response
        result_str = str(result)

        return [TextContent(type="text", text=result_str)]

    except Exception as e:
        import traceback
        error_msg = f"Error executing tool '{name}': {str(e)}\n{traceback.format_exc()}"
        return [TextContent(type="text", text=error_msg)]


async def main():
    """Start the MCP server."""
    print("Starting MCP-KE server...")
    print(f"Auto-discovering tools from tools/ and agent_tools/ directories...")

    # Trigger tool discovery
    get_tools()

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
