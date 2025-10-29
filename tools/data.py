"""
Load observational data
"""

import numpy as np
from .path_utils import get_input_path

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
    try:
        # Get the full input path (handles input/ directory lookup)
        full_path = get_input_path(filepath)

        k, Pk, σPk = np.loadtxt(full_path).T
        print(f"Loaded observational data from: {full_path}")
        print(f"  {len(k)} points")
        print(f"  k range: [{k.min():.2e}, {k.max():.2e}] h/Mpc")
        return k, Pk, σPk
    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None, None