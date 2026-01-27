import asyncio
import importlib
import inspect
import pkgutil
import sys
from typing import Any

from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio

import tools
import agent_tools

app = Server("mcp-ke")
_TOOLS_CACHE = None


def discover_tools() -> dict[str, callable]:
    discovered = {}
    for package in [tools, agent_tools]:
        for _, modname, _ in pkgutil.walk_packages(package.__path__, f'{package.__name__}.', lambda x: None):
            try:
                module = importlib.import_module(modname)
                for name, obj in inspect.getmembers(module, callable):
                    if hasattr(obj, '__wrapped__') or hasattr(obj, 'name'):
                        tool_name = getattr(obj, 'name', name)
                        if tool_name != "final_answer":
                            discovered[tool_name] = obj
            except Exception:
                continue
    return discovered


def build_mcp_tool(name: str, func: callable) -> Tool:
    doc = getattr(func, 'description', None)
    if not doc:
        doc = inspect.getdoc(func)
    if not doc:
        doc = name

    inputs = getattr(func, 'inputs', {})
    properties = {}
    required = []

    for param_name, param_info in inputs.items():
        properties[param_name] = {"type": param_info.get("type", "string")}
        if not param_info.get("nullable", False):
            required.append(param_name)

    return Tool(name=name, description=doc, inputSchema={"type": "object", "properties": properties, "required": required})


def get_tools() -> dict[str, callable]:
    global _TOOLS_CACHE
    if _TOOLS_CACHE is None:
        _TOOLS_CACHE = discover_tools()
    return _TOOLS_CACHE


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [build_mcp_tool(name, func) for name, func in get_tools().items()]


# Skip MCP schema validation - smolagents uses 'type: object' for arrays, which strict JSON schema rejects
@app.call_tool(validate_input=False)
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    tools_dict = get_tools()
    if name not in tools_dict:
        return [TextContent(type="text", text=f"Error: Tool '{name}' not found")]
    try:
        result = tools_dict[name](**arguments)
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {e}")]


async def _main():
    get_tools()
    async with mcp.server.stdio.stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())


def main():
    asyncio.run(_main())


if __name__ == "__main__":
    main()
