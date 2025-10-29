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

    # Otherwise, look in input/ directory in cwd
    input_dir = os.path.join(os.getcwd(), 'input')

    if not os.path.isdir(input_dir):
        raise FileNotFoundError(
            f"Input directory not found: {input_dir}\n"
            f"Please create an 'input/' directory in your working directory "
            f"and place your data files there."
        )

    input_path = os.path.join(input_dir, filename)

    if not os.path.exists(input_path):
        raise FileNotFoundError(
            f"File '{filename}' not found in input directory: {input_dir}\n"
            f"Available files: {', '.join(os.listdir(input_dir)) if os.listdir(input_dir) else '(none)'}"
        )

    return input_path


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

    # Otherwise, save to out/ directory in cwd
    output_dir = os.path.join(os.getcwd(), 'out')

    if not os.path.isdir(output_dir):
        raise FileNotFoundError(
            f"Output directory not found: {output_dir}\n"
            f"Please create an 'out/' directory in your working directory."
        )

    return os.path.join(output_dir, filename)
