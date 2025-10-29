#!/usr/bin/env python3
"""MCP-KE Server - Wraps tools from config.yaml as MCP tools"""
import asyncio
from typing import Any

from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio

from ke_mcp.src import build_tool, config_loader, validator, tool_handler

app = Server(config_loader.get_server_config()["name"])


@app.list_tools()
async def list_tools() -> list[Tool]:
    """Return available tools from config"""
    tools = config_loader.get_all_tools()
    return [build_tool.from_config(tid, cfg) for tid, cfg in tools.items()]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute tool and return response"""
    return tool_handler.handle_tool_call(name, arguments)


async def main():
    """Start MCP server with validation"""
    validator.validate_or_exit()
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
