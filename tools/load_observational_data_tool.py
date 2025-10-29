import numpy as np
from smolagents import tool

@tool
def create_theory_k_grid() -> object:
    """
    Create standard k-grid for theoretical power spectrum predictions.
    
    Creates a 300-point logarithmic k-grid from 0.0001 to 10 h/Mpc for computing
    theoretical models. ALWAYS call this FIRST before computing models.
    
    DO NOT use observational k-bins (19 points, 0.2-2.5 h/Mpc) for theoretical models.
    
    Args: None needed
    Returns:
        numpy array of k values in h/Mpc (300 points, logarithmically spaced)
    """
    k_theory = np.logspace(-4, np.log10(10), 300)
    print(f"Created theory k-grid: {len(k_theory)} points, range [{k_theory.min():.2e}, {k_theory.max():.2e}] h/Mpc")
    return k_theory

@tool
def load_observational_data(filepath: str) -> tuple:
    """
    Load observational data from text file.

    Args:
        filepath: Filename or path to the data file. If just a filename (e.g., 'DR14_pm3d_19kbins.txt'),
                 looks for it in the 'input/' directory in your current working directory.
                 If an absolute path or contains path separators, uses it as-is.

                 IMPORTANT: You must have an 'input/' directory in your working directory
                 with your data files in it.

    Returns:
        Tuple of three numpy arrays (all dtype float64):
            [0]: k - wavenumber values in h/Mpc
            [1]: P(k) - power spectrum values in (Mpc/h)^3
            [2]: σP(k) - error/uncertainty values in (Mpc/h)^3
        Returns (None, None, None) if loading fails
    """
    from .data import load_observational_data as load_obs_data
    return load_obs_data(filepath)