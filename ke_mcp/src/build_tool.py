"""Build MCP Tool schema from config"""

from mcp.types import Tool


def from_config(tool_id: str, tool_config: dict) -> Tool:
    """
    Convert tool config to MCP Tool schema.

    Reads parameters and builds JSON Schema for MCP.
    """
    properties = {}
    required = []

    for param_name, param_config in tool_config["parameters"].items():
        prop = {"type": param_config["type"]}

        if "description" in param_config:
            prop["description"] = param_config["description"]
        if "enum" in param_config:
            prop["enum"] = param_config["enum"]
        if "default" in param_config:
            prop["default"] = param_config["default"]

        properties[param_name] = prop

        if param_config.get("required", False):
            required.append(param_name)

    description = tool_config["description"]
    if tool_config.get("examples"):
        examples = "\n".join(f"  - {ex}" for ex in tool_config["examples"])
        description += f"\n\nExamples:\n{examples}"

    return Tool(
        name=tool_config["tool_name"],
        description=description,
        inputSchema={
            "type": "object",
            "properties": properties,
            "required": required
        },
    )
