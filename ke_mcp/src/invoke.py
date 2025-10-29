import importlib
from typing import Any, Tuple


def validate_entry_point(entry_point: str) -> Tuple[bool, str]:
    """
    Check if entry_point can be imported and called.

    Returns: (success, error_message)
    """
    try:
        module_path, callable_name = entry_point.rsplit(".", 1)
        module = importlib.import_module(module_path)
        if not hasattr(module, callable_name):
            return False, f"Module '{module_path}' has no attribute '{callable_name}'"
        func = getattr(module, callable_name)
        if not callable(func):
            return False, f"{entry_point} is not callable"
        return True, ""
    except ValueError:
        return False, f"Invalid entry_point format: {entry_point} (expected 'module.path.callable')"
    except ImportError as e:
        return False, f"Cannot import module: {e}"
    except Exception as e:
        return False, f"Validation error: {e}"


def call(entry_point: str, arguments: dict) -> Any:
    """
    Dynamically import and call entry_point with arguments.

    entry_point: "module.path.callable_name"
    arguments: kwargs to pass to callable

    Returns: Whatever the callable returns
    Raises: ImportError, AttributeError, or whatever the callable raises
    """
    module_path, callable_name = entry_point.rsplit(".", 1)
    module = importlib.import_module(module_path)
    func = getattr(module, callable_name)
    return func(**arguments)
