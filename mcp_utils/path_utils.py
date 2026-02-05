"""
Utilities for managing input/output directory paths for MCP tools.

Users are expected to create input/ and out/ directories in their working directory.
Tools will look for data files in input/ and save results to out/.
"""

import os

def get_input_path(filename):
    """
    Get the full path for an input data file.

    If filename is just a filename (no directory separators), looks for it in
    the 'input/' directory in the current working directory.

    If filename contains path separators or is an absolute path, returns it as-is
    for backwards compatibility.

    Args:
        filename: Name of the file or full path

    Returns:
        str: Full path to the input file

    Raises:
        FileNotFoundError: If input/ directory doesn't exist or file not found
    """
    # If it's an absolute path or contains path separators, use as-is
    if os.path.isabs(filename) or os.sep in filename or (os.altsep and os.altsep in filename):
        if not os.path.exists(filename):
            raise FileNotFoundError(f"File not found: {filename}")
        return filename

    # First, try input/ directory in cwd
    input_dir = os.path.join(os.getcwd(), 'input')
    if os.path.isdir(input_dir):
        input_path = os.path.join(input_dir, filename)
        if os.path.exists(input_path):
            return input_path

    # Fallback: check package's data/ directory (for editable/source installs)
    pkg_data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    pkg_data_path = os.path.join(pkg_data_dir, filename)
    if os.path.exists(pkg_data_path):
        return pkg_data_path

    # Fallback: check installed data-files location (for pip installs)
    import sys
    installed_data_dir = os.path.join(sys.prefix, 'mcp_ke_data')
    installed_data_path = os.path.join(installed_data_dir, filename)
    if os.path.exists(installed_data_path):
        return installed_data_path

    # File not found in any location
    locations = [f"input/ ({input_dir})"]
    if os.path.isdir(pkg_data_dir):
        locations.append(f"package data/ ({pkg_data_dir})")
    if os.path.isdir(installed_data_dir):
        locations.append(f"installed data ({installed_data_dir})")
    raise FileNotFoundError(
        f"File '{filename}' not found in: {', '.join(locations)}"
    )


def get_output_dir():
    return os.environ.get('MCP_OUTPUT_DIR') or os.path.join(os.getcwd(), 'mcp_ke_output')


def get_output_path(filename=None):
    """
    Get the full path for an output file.

    If filename is just a filename (no directory separators), saves it in
    the 'out/' directory in the current working directory.

    If filename contains path separators or is an absolute path, returns it as-is
    for backwards compatibility.

    Args:
        filename: Optional name of the file or full path. If None, returns None.

    Returns:
        str: Full path to the output file, or None if filename is None

    Raises:
        FileNotFoundError: If out/ directory doesn't exist
    """
    if filename is None:
        return None

    # If it's an absolute path or contains path separators, use as-is
    if os.path.isabs(filename) or os.sep in filename or (os.altsep and os.altsep in filename):
        return filename

    output_dir = get_output_dir()

    if not os.path.isdir(output_dir):
        raise FileNotFoundError(
            f"Output directory not found: {output_dir}\n"
            f"Please create an 'out/' directory in your working directory."
        )

    return os.path.join(output_dir, filename)
