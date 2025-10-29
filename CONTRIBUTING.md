# Contributing

MCP-KE is a registry. Tool code lives in your repository.

## Registration

1. Fork this repo
2. Add entry to `config.yaml`
3. Submit PR

## Config Format

```yaml
tools:
  your_tool:
    type: python_callable
    entry_point: your_module.run  # Must accept **kwargs
    repository: https://github.com/YourOrg/tool
    contact: team@example.com

    tool_name: tool_name
    description: What it does
    parameters:
      param:
        type: string
        required: true
        description: Parameter description
```

## Requirements

- Provide Python package with callable entry point
- Entry point accepts `**kwargs` and returns result
- Repository is publicly accessible
- Contact email provided

## Entry Point Function

```python
# your_module.py in your repository
def run(**kwargs) -> str:
    """
    Your tool logic here.

    If your tool has internal dependencies (databases, MCP servers, etc.),
    start them inside this function.
    """
    # Handle your internal complexity here
    # Start services, connect to databases, etc.

    result = your_logic(**kwargs)
    return result
```

**Complex tools:** If your tool has multiple components, handle startup in your entry point:

```python
import subprocess
import time

def run(question: str) -> str:
    # Start internal services if needed
    server = subprocess.Popen(["python", "-m", "internal.server"])
    time.sleep(2)  # Wait for startup

    # Your tool logic
    result = process(question)

    # Cleanup
    server.terminate()
    return result
```

## Maintenance

Each team maintains their own code in their own repository.

MIT License
