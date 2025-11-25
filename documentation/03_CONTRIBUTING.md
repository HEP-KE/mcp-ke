# Contributing to MCP-KE

## Adding a New Domain Tool

### Quick Start

1. Create a new file in `tools/` (e.g., `tools/my_tool.py`)
2. Decorate your function with `@tool` from smolagents
3. Add a docstring to your function with a brief description of the tool, Args, and Returns details
4. Add type hints for function parameters and return (supports: str, int, float, bool, dict, list, object)
5. Done - the server auto-discovers the new tool on startup

### Example

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

## Extension Points

### Adding a New Domain Tool (Detailed)

**Example**: Add a tool for computing distance modulus

```python
# In tools/distance_tools.py

from smolagents import tool

@tool
def compute_distance_modulus(z: float, model_params: dict) -> float:
    """
    Compute distance modulus at redshift z for given cosmology.

    Args:
        z: Redshift
        model_params: Cosmology parameter dict (from LCDM, wCDM, etc.)

    Returns:
        Distance modulus in magnitudes
    """
    from codes.distances import compute_distance_modulus as compute_dm
    return compute_dm(z, model_params)
```

**That's it!** Server auto-discovers on next startup.

**Add to `tools/__init__.py`** (optional, for documentation):

```python
from .distance_tools import compute_distance_modulus

__all__ = [
    ...,
    "compute_distance_modulus",
]
```

### Adding a New Agent Tool

**Example**: Create a model fitting agent

```python
# In agent_tools/fitting_agent.py

from smolagents import CodeAgent, tool
from .llm_helper import create_openai_compatible_llm

@tool
def model_fitting_agent(
    query: str,
    api_key: str,
    llm_url: str,
    model_id: str
) -> str:
    """
    Fit cosmological models to observational data using MCMC.

    Args:
        query: Fitting task description
        api_key: API key for LLM
        llm_url: LLM API endpoint
        model_id: Model identifier

    Returns:
        Fitting results and parameter constraints
    """
    model = create_openai_compatible_llm(api_key, llm_url, model_id)

    # Import relevant tools for this agent
    from tools import (
        load_observational_data,
        LCDM,
        compute_power_spectrum,
    )

    # Create custom MCMC tools
    @tool
    def run_mcmc_chain(params, data, n_steps):
        # Implementation here
        pass

    agent = CodeAgent(
        model=model,
        tools=[
            load_observational_data,
            LCDM,
            compute_power_spectrum,
            run_mcmc_chain,
        ],
        max_steps=50,
        name="fitting_agent",
        instructions="Your fitting workflow instructions here..."
    )

    return str(agent.run(query))
```

**Auto-discovered!** No registration needed.

### Modifying Tool Discovery

To customize which tools are exposed, edit `mcp_server.py:discover_tools()`:

```python
# Example: Filter out agent tools
discovered_tools = {}
for package in [tools]:  # Remove agent_tools from list
    # ... discovery logic
```

Or filter by name:

```python
# Example: Only expose tools starting with "plot_"
if not tool_name.startswith("plot_"):
    continue
```

## Best Practices

### Tool Design

1. **Keep tools atomic**: Each tool should do one thing well
2. **Use type hints**: They become part of the JSON schema
3. **Write clear docstrings**: They appear in MCP tool descriptions
4. **Return simple types**: Prefer strings, dicts, and paths over complex objects
5. **Handle errors gracefully**: Return error messages as strings when appropriate

### Code Organization

1. **Thin wrappers**: Keep tool functions simple, put logic in `codes/`
2. **Reusable implementations**: Core logic in `codes/` should work without MCP
3. **Consistent paths**: Use `mcp_utils.path_utils` for file paths
4. **File-based state**: Agents should pass file paths, not large data structures

### Testing

1. **Unit test domain tools**: Test without API keys or network calls
2. **Integration test agent tools**: Use real LLMs but mark tests appropriately
3. **Mock external dependencies**: Use fixtures for CLASS computations when possible
4. **Test error cases**: Ensure tools handle invalid inputs gracefully

## License

MIT License
