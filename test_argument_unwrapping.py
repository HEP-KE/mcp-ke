#!/usr/bin/env python3
"""Test script to verify argument unwrapping logic works correctly."""

import json
import inspect
from tools.cosmology_models_tool import nu_mass

def unwrap_arguments(func, arguments):
    """Simulate the unwrapping logic from mcp_server.py"""
    func_name = getattr(func, 'name', getattr(func, '__name__', str(func)))
    print(f"[DEBUG] Tool: {func_name}")
    print(f"[DEBUG] Raw arguments: {arguments}")
    print(f"[DEBUG] Arguments type: {type(arguments)}")

    # Unwrap args/kwargs if the MCP client wrapped them
    if isinstance(arguments, dict) and set(arguments.keys()) <= {"args", "kwargs"}:
        args = arguments.get("args", [])
        kwargs = arguments.get("kwargs", {})

        # Parse JSON strings if provided
        if isinstance(kwargs, str):
            try:
                kwargs = json.loads(kwargs)
            except json.JSONDecodeError:
                pass

        if isinstance(args, str):
            try:
                args = json.loads(args)
            except json.JSONDecodeError:
                pass

        # Merge kwargs with converted positional args
        if args and not kwargs:
            # Check if this is a smolagents tool (has 'forward' method)
            if hasattr(func, 'forward'):
                # Get the actual tool function's signature
                actual_func = getattr(func, 'forward', func)
                sig = inspect.signature(actual_func)
                param_names = [
                    name for name, param in sig.parameters.items()
                    if name not in ('self', 'cls')
                    and param.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
                ]
            else:
                sig = inspect.signature(func)
                param_names = [
                    name for name, param in sig.parameters.items()
                    if name not in ('self', 'cls')
                    and param.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
                ]

            if isinstance(args, list):
                if len(args) > 0 and len(param_names) > 0:
                    kwargs = dict(zip(param_names, args))
            elif isinstance(args, str) and len(param_names) > 0:
                kwargs = {param_names[0]: args}

        arguments = kwargs if kwargs else {}

    print(f"[DEBUG] Final arguments to pass: {arguments}")
    print(f"[DEBUG] Function signature: {inspect.signature(func)}")
    return arguments


# Test cases
print("=" * 60)
print("Test 1: Empty args and kwargs (for LCDM)")
print("=" * 60)
test_args = {"args": [], "kwargs": {}}
unwrapped = unwrap_arguments(nu_mass, test_args)
print(f"Result: {unwrapped}\n")

print("=" * 60)
print("Test 2: Single positional arg as list (for nu_mass)")
print("=" * 60)
test_args = {"args": [0.1], "kwargs": {}}
unwrapped = unwrap_arguments(nu_mass, test_args)
print(f"Result: {unwrapped}")
print(f"Calling nu_mass with unwrapped args...")
try:
    result = nu_mass(**unwrapped)
    print(f"Success! Result: {result}\n")
except Exception as e:
    print(f"Error: {e}\n")

print("=" * 60)
print("Test 3: Multiple positional args as list")
print("=" * 60)
test_args = {"args": [0.15, 2], "kwargs": {}}
unwrapped = unwrap_arguments(nu_mass, test_args)
print(f"Result: {unwrapped}")
print(f"Calling nu_mass with unwrapped args...")
try:
    result = nu_mass(**unwrapped)
    print(f"Success! Result: {result}\n")
except Exception as e:
    print(f"Error: {e}\n")

print("=" * 60)
print("Test 4: kwargs as JSON string")
print("=" * 60)
test_args = {"args": [], "kwargs": '{"sum_mnu_eV": 0.2, "N_species": 3}'}
unwrapped = unwrap_arguments(nu_mass, test_args)
print(f"Result: {unwrapped}")
print(f"Calling nu_mass with unwrapped args...")
try:
    result = nu_mass(**unwrapped)
    print(f"Success! Result: {result}\n")
except Exception as e:
    print(f"Error: {e}\n")
