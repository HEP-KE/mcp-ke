"""Config structure validation"""
from ke_mcp.src.schema import REQUIRED_TOOL_FIELDS, REQUIRED_SERVER_FIELDS
from ke_mcp.src.param_validator import validate_all_parameters


def validate_tool(tool_id: str, tool_config: dict) -> list[str]:
    """Validate tool configuration"""
    errors = []

    if not isinstance(tool_config, dict):
        return [f"{tool_id}: Must be a dict"]

    # Check required fields exist
    for field in REQUIRED_TOOL_FIELDS:
        if field not in tool_config:
            errors.append(f"{tool_id}: Missing '{field}'")

    # Validate parameters if present
    if "parameters" in tool_config:
        errors.extend(validate_all_parameters(tool_id, tool_config["parameters"]))

    return errors


def validate_server(server_config: dict) -> list[str]:
    """Validate server configuration"""
    errors = []

    if not isinstance(server_config, dict):
        return ["server: Must be a dict"]

    for field in REQUIRED_SERVER_FIELDS:
        if field not in server_config:
            errors.append(f"server: Missing '{field}'")

    return errors


def validate_config_structure(config: dict) -> list[str]:
    """Validate entire config structure"""
    errors = []

    if not isinstance(config, dict):
        return ["Config must be a dict"]

    if "tools" not in config:
        errors.append("Missing 'tools' key")
    elif isinstance(config["tools"], dict):
        for tool_id, tool_config in config["tools"].items():
            errors.extend(validate_tool(tool_id, tool_config))

    if "server" not in config:
        errors.append("Missing 'server' key")
    else:
        errors.extend(validate_server(config["server"]))

    return errors
