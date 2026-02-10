import json
import numpy as np
from smolagents import tool
from mcp_utils.session import get_session

@tool
def create_theory_k_grid() -> str:
    """
    Create standard k-grid for theoretical power spectrum predictions.

    Creates a 300-point logarithmic k-grid from 0.0001 to 10 h/Mpc for computing
    theoretical models. ALWAYS call this FIRST before computing models.

    DO NOT use observational k-bins (19 points, 0.2-2.5 h/Mpc) for theoretical models.

    Args: None needed
    Returns:
        JSON with dataset_name referencing a numpy array of k values
        in h/Mpc (300 points, logarithmically spaced). Use dataset_name in
        subsequent tool calls.
    """
    session = get_session()
    k_theory = np.logspace(-4, np.log10(10), 300)
    dataset_name, info = session.load_dataset(k_theory, name="k_theory")
    return json.dumps({"dataset_name": dataset_name, "row_count": info.row_count}, indent=2)

@tool
def load_observational_data(filepath: str) -> str:
    """
    Load observational data from text file.

    Args:
        filepath: Filename or path to the data file. If just a filename (e.g., 'DR14_pm3d_19kbins.txt'),
                 looks for it in the 'input/' directory in your current working directory.
                 If an absolute path or contains path separators, uses it as-is.

                 IMPORTANT: You must have an 'input/' directory in your working directory
                 with your data files in it.

    Returns:
        JSON with three dataset_names:
            - k_obs: wavenumber values in h/Mpc
            - Pk_obs: power spectrum values in (Mpc/h)^3
            - Pk_obs_err: error/uncertainty values in (Mpc/h)^3
        Use these dataset_names in subsequent tool calls.
    """
    import os
    from codes.data import load_observational_data as load_obs_data
    session = get_session()
    k, Pk, err = load_obs_data(filepath)

    base = os.path.splitext(os.path.basename(filepath))[0]
    k_name, k_info = session.load_dataset(k, path=filepath, name=f"{base}_k")
    Pk_name, Pk_info = session.load_dataset(Pk, path=filepath, name=f"{base}_Pk")
    err_name, err_info = session.load_dataset(err, path=filepath, name=f"{base}_err")

    return json.dumps({
        "k_obs": k_name,
        "Pk_obs": Pk_name,
        "Pk_obs_err": err_name,
        "row_count": k_info.row_count
    }, indent=2)