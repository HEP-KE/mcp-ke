# Contributing

## Adding a New Tool

1. Create a new file in `tools/` (e.g., `tools/my_tool.py`)
2. Decorate your function with `@tool` from smolagents
3. Done - the server auto-discovers it on startup

## Example

```python
from smolagents import tool

@tool
def my_analysis_tool(parameter: str, threshold: float = 0.5) -> dict:
    """
    Brief description of what your tool does.

    Args:
        parameter: Description of parameter
        threshold: Optional threshold value

    Returns:
        dict: Results dictionary
    """
    result = your_logic(parameter, threshold)
    return result
```

## Requirements

- **Decorator**: Use `@tool` from smolagents (or any callable with `name` or `__wrapped__` attributes)
- **Docstring**: Required - used as tool description in MCP
- **Type hints**: Recommended for parameter schema generation (supports: str, int, float, bool, dict, list, object)
- **Return value**: Any type (automatically converted to string by MCP server)

MIT License
