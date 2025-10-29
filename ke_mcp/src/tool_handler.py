"""Tool invocation and response handling"""
import json
import traceback
from typing import Any

from mcp.types import TextContent
from ke_mcp.src import invoke, config_loader


def create_error_response(message: str, **extra) -> list[TextContent]:
    """Create standardized error response"""
    response = {"status": "error", "error": message, **extra}
    return [TextContent(type="text", text=json.dumps(response, indent=2))]


def create_success_response(result: Any, tool_name: str) -> list[TextContent]:
    """Create standardized success response"""
    response = {"status": "success", "result": str(result), "tool": tool_name}
    return [TextContent(type="text", text=json.dumps(response, indent=2))]


def handle_tool_call(name: str, arguments: dict) -> list[TextContent]:
    """Execute tool and return formatted response"""
    tool_config = config_loader.get_tool_config(name)

    if not tool_config:
        tools = config_loader.get_all_tools()
        available = [cfg["tool_name"] for cfg in tools.values()]
        return create_error_response(
            f"Unknown tool: {name}",
            available_tools=available
        )

    try:
        result = invoke.call(tool_config["entry_point"], arguments)
        return create_success_response(result, name)
    except Exception as e:
        return create_error_response(
            str(e),
            type=type(e).__name__,
            traceback=traceback.format_exc()
        )
