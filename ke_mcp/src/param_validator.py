"""Parameter validation logic"""
from ke_mcp.src.schema import REQUIRED_PARAM_FIELDS, OPTIONAL_PARAM_FIELDS


def validate_parameter(tool_id: str, param_name: str, param_config: dict) -> list[str]:
    """Validate single parameter configuration"""
    errors = []

    if not isinstance(param_config, dict):
        return [f"{tool_id}.{param_name}: Must be a dict"]

    # Check required fields
    for field, expected_type in REQUIRED_PARAM_FIELDS.items():
        if field not in param_config:
            errors.append(f"{tool_id}.{param_name}: Missing '{field}'")
        elif not isinstance(param_config[field], expected_type):
            errors.append(f"{tool_id}.{param_name}.{field}: Must be {expected_type.__name__}")

    # Check optional fields
    for field, expected_type in OPTIONAL_PARAM_FIELDS.items():
        if field in param_config:
            if not isinstance(param_config[field], expected_type):
                errors.append(f"{tool_id}.{param_name}.{field}: Wrong type")

    return errors


def validate_all_parameters(tool_id: str, parameters: dict) -> list[str]:
    """Validate all parameters for a tool"""
    errors = []

    if not isinstance(parameters, dict):
        return [f"{tool_id}.parameters: Must be a dict"]

    for param_name, param_config in parameters.items():
        errors.extend(validate_parameter(tool_id, param_name, param_config))

    return errors
