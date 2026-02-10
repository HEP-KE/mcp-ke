"""
Load observational data
"""

import numpy as np
from mcp_utils import get_input_path

def load_observational_data(filepath):
    """
    Load observational data from text file.

    Args:
        filepath: Path to the data file. If just a filename (no path separators),
                 looks for it in the 'input/' directory in the current working directory.
                 If an absolute path or contains path separators, uses it as-is.

    Returns:
        Tuple of (k, P(k), error) arrays or (None, None, None) if loading fails
    """
    full_path = get_input_path(filepath)
    k, Pk, σPk = np.loadtxt(full_path).T
    return k, Pk, σPk