# Contributing

## Adding a New Tool

1. Create a new file in `tools/` (e.g., `tools/my_tool.py`)
2. Decorate your function with `@tool` from smolagents
3. Add a docstring to your function with a brief description of the tool, Args, and Returns details
4. Add type hints for function parameters and return (supports: str, int, float, bool, dict, list, object)
5. Done - the server auto-discovers the new tool on startup

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

MIT License
