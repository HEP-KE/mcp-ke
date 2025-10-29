"""Config schema definitions"""

REQUIRED_TOOL_FIELDS = {
    "repository": str,
    "version": str,
    "contact": str,
    "purpose": str,
    "tool_name": str,
    "entry_point": str,
    "description": str,
    "parameters": dict,
}

REQUIRED_PARAM_FIELDS = {
    "type": str,
    "required": bool,
}

OPTIONAL_PARAM_FIELDS = {
    "description": str,
    "enum": list,
    "default": (str, int, float, bool),
}

REQUIRED_SERVER_FIELDS = {
    "name": str,
    "version": str,
}
