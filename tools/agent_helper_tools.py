"""
Agent helper tools for saving/loading arrays and dictionaries between agents.

These tools help agents share data by saving/loading files in the 'out/' directory
in the user's current working directory.
"""

import os
import json
import glob
import numpy as np
from smolagents import tool
from mcp_utils import get_output_path


def get_out_dir():
    """Get the out/ directory path and verify it exists."""
    out_dir = os.environ.get('MCP_OUTPUT_DIR') or os.path.join(os.getcwd(), 'mcp_ke_output')
    if not os.path.isdir(out_dir):
        raise FileNotFoundError(
            f"Output directory not found: {out_dir}\n"
            f"Please create an 'out/' directory in your working directory."
        )
    return out_dir


@tool
def list_agent_files() -> list:
    """
    List all files in the out/ directory with their absolute paths.

    Returns:
        list: List of absolute file paths (str) in the out/ directory

    Raises:
        FileNotFoundError: If out/ directory doesn't exist
    """
    out_dir = get_out_dir()
    files = glob.glob(os.path.join(out_dir, '*'))
    abs_paths = [os.path.abspath(f) for f in files]
    return abs_paths


@tool
def save_array(array: object, filename: str) -> str:
    """
    Save a numpy array to the out/ directory for sharing between agents.

    Args:
        array: Numpy array to save
        filename: Filename only (with or without .npy extension, no directory path)

    Returns:
        str: Absolute path to saved .npy file

    Raises:
        FileNotFoundError: If out/ directory doesn't exist
        ValueError: If filename has wrong extension
    """
    base_filename = os.path.basename(filename)
    if '.' in base_filename:
        if not base_filename.endswith('.npy'):
            raise ValueError(f"save_array() only accepts .npy extension. Got: {base_filename}")
    else:
        base_filename = f"{base_filename}.npy"

    filepath = get_output_path(base_filename)
    np.save(filepath, array)
    return filepath


@tool
def load_array(filename: str) -> object:
    """
    Load a numpy array from the out/ directory.

    Args:
        filename: Filename only (with or without .npy extension, no directory path)

    Returns:
        numpy array loaded from file

    Raises:
        FileNotFoundError: If out/ directory doesn't exist or file not found
    """
    base_filename = os.path.basename(filename)
    if not base_filename.endswith('.npy'):
        base_filename = base_filename + '.npy'

    out_dir = get_out_dir()
    final_path = os.path.join(out_dir, base_filename)

    if not os.path.exists(final_path):
        raise FileNotFoundError(
            f"File '{base_filename}' not found in out/ directory: {out_dir}\n"
            f"Use list_agent_files() to see available files."
        )

    array = np.load(final_path)
    return array


@tool
def save_dict(data: dict, filename: str) -> str:
    """
    Save a dictionary to the out/ directory (arrays saved as separate .npy files).

    Args:
        data: Dictionary where keys are strings and values are either:
            - Numpy arrays (saved as separate .npy files)
            - Primitives: int, float, str, bool (saved in JSON)
        filename: Filename only (with or without .json extension, no directory path)

    Returns:
        str: Absolute path to saved metadata JSON file

    Raises:
        FileNotFoundError: If out/ directory doesn't exist
        ValueError: If filename has wrong extension
    """
    base_filename = os.path.basename(filename)
    if '.' in base_filename:
        if not base_filename.endswith('.json'):
            raise ValueError(f"save_dict() only accepts .json extension. Got: {base_filename}")
        base_filename = base_filename.replace('.json', '')

    metadata = {}
    for key, value in data.items():
        if isinstance(value, np.ndarray):
            array_name = f"{base_filename}_{key.replace(' ', '_').replace('(', '').replace(')', '').replace('=', '_')}.npy"
            array_path = save_array(value, array_name)
            metadata[key] = {'type': 'array', 'path': array_path}
        else:
            metadata[key] = {'type': 'primitive', 'value': value}

    metadata_filename = f'{base_filename}_metadata.json' if not base_filename.endswith('_metadata') else f'{base_filename}.json'
    metadata_path = get_output_path(metadata_filename)

    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    return metadata_path


@tool
def load_dict(filename: str) -> dict:
    """
    Load a dictionary from the out/ directory (reconstructs arrays from .npy files).

    Args:
        filename: Filename only (with or without .json/_metadata.json suffix, no directory path)

    Returns:
        dict: Dictionary where:
            - Keys (str): Original dictionary keys
            - Values: Either numpy arrays (reconstructed from .npy files) or primitives (int/float/str/bool)

    Raises:
        FileNotFoundError: If out/ directory doesn't exist or file not found
    """
    base_filename = os.path.basename(filename)
    if not base_filename.endswith('.json'):
        base_filename = base_filename + '_metadata.json' if not base_filename.endswith('_metadata') else base_filename + '.json'

    out_dir = get_out_dir()
    final_path = os.path.join(out_dir, base_filename)

    if not os.path.exists(final_path):
        raise FileNotFoundError(
            f"File '{base_filename}' not found in out/ directory: {out_dir}\n"
            f"Use list_agent_files() to see available files."
        )

    with open(final_path, 'r') as f:
        metadata = json.load(f)

    result = {}
    for key, info in metadata.items():
        if info['type'] == 'array':
            result[key] = load_array(info['path'])
        else:
            result[key] = info['value']

    return result
