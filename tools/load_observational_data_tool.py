import json
import os
import numpy as np
from smolagents import tool
from mcp_utils.session import get_session
from mcp_utils import get_input_dir

EBOSS_FILE = "DR14_pm3d_19kbins.txt"


def _get_available_input_files():
    """Scan input directory for available data files."""
    try:
        input_dir = get_input_dir()
        files = [f for f in os.listdir(input_dir)
                 if os.path.isfile(os.path.join(input_dir, f))
                 and not f.startswith('.')]
        return sorted(files)
    except Exception:
        return []


_AVAILABLE_FILES = _get_available_input_files()


@tool
def load_eboss_data() -> str:
    """
    Load eBOSS DR14 Lyman-alpha forest power spectrum data.

    Loads the bundled eBOSS DR14 observational P(k) data with 19 k-bins.
    No arguments needed - data is included with the package.

    Returns:
        JSON with dataset_names for the loaded data:
            - k_obs: wavenumber values in h/Mpc (19 bins, 0.02-0.35 h/Mpc)
            - Pk_obs: power spectrum values in (Mpc/h)^3
            - Pk_obs_err: error/uncertainty values in (Mpc/h)^3
        Use these dataset_names in subsequent tool calls.
    """
    from codes.data import load_observational_data as load_obs_data
    session = get_session()
    k, Pk, err = load_obs_data(EBOSS_FILE)

    k_name, k_info = session.load_dataset(k, path=EBOSS_FILE, name="eboss_k")
    Pk_name, _ = session.load_dataset(Pk, path=EBOSS_FILE, name="eboss_Pk")
    err_name, _ = session.load_dataset(err, path=EBOSS_FILE, name="eboss_err")

    return json.dumps({
        "status": "success",
        "datasets": [k_name, Pk_name, err_name],
        "columns": ["k (h/Mpc)", "P(k) (Mpc/h)^3", "P(k)_err (Mpc/h)^3"],
        "row_count": k_info.row_count,
        "source": "eBOSS DR14 Lyman-alpha forest",
        "usage": "Refer to these datasets by their names in subsequent tools.",
    }, indent=2)


@tool
def create_theory_k_grid(
    k_min: float,
    k_max: float,
    n_points: int = 300,
) -> str:
    """
    Create k-grid for theoretical power spectrum predictions.

    Creates a logarithmically-spaced k-grid for computing theoretical models.
    ALWAYS call this FIRST before computing models.

    DO NOT use observational k-bins for theoretical models.

    Args:
        k_min: Minimum k value in h/Mpc (e.g., 0.0001)
        k_max: Maximum k value in h/Mpc (e.g., 10.0). Note: when using
            compute_power_spectrum, P_k_max_h_Mpc must be greater than k_max.
        n_points: Number of logarithmically-spaced points (default: 300)

    Returns:
        JSON with dataset_name referencing a numpy array of k values
        in h/Mpc. Use dataset_name in subsequent tool calls.
    """
    session = get_session()
    k_theory = np.logspace(np.log10(k_min), np.log10(k_max), n_points)
    dataset_name, info = session.load_dataset(k_theory, name="k_theory")
    return json.dumps({
        "status": "success",
        "datasets": [dataset_name],
        "columns": ["k (h/Mpc)"],
        "row_count": info.row_count,
        "k_range": [k_min, k_max],
        "usage": "Refer to this dataset by its name in subsequent tools.",
    }, indent=2)

@tool
def list_input_files() -> str:
    """
    List available data files on the server.

    Call this to discover what files can be loaded with load_observational_data.

    Returns:
        JSON with list of available filenames in the server's input directory.
    """
    return json.dumps({
        "status": "success",
        "files": _AVAILABLE_FILES,
        "usage": "Pass any of these filenames to load_observational_data()."
    }, indent=2)


@tool
def load_observational_data(filename: str) -> str:
    """
    Load P(k) power spectrum data into session.

    Args:
        filename: Name of data file to load. Call list_input_files() to see available files.
            Just pass the filename string - this tool finds the file on the server.

    Returns:
        JSON with three dataset_names for P(k) data stored in session.
        Use these dataset_names in run_mcmc_cosmology or visualization tools.
    """
    from codes.data import load_observational_data as load_obs_data
    session = get_session()
    k, Pk, err = load_obs_data(filename)

    base = os.path.splitext(os.path.basename(filename))[0]
    k_name, k_info = session.load_dataset(k, path=filename, name=f"{base}_k")
    Pk_name, _ = session.load_dataset(Pk, path=filename, name=f"{base}_Pk")
    err_name, _ = session.load_dataset(err, path=filename, name=f"{base}_err")

    return json.dumps({
        "status": "success",
        "datasets": [k_name, Pk_name, err_name],
        "columns": ["k (h/Mpc)", "P(k) (Mpc/h)^3", "P(k)_err (Mpc/h)^3"],
        "row_count": k_info.row_count,
        "source": filename,
        "usage": "Refer to these datasets by their names in subsequent tools.",
    }, indent=2)