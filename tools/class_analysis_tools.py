import json
from smolagents import tool
from mcp_utils.session import get_session

@tool
def compute_power_spectrum(
    k_values: str,
    h: float,
    Omega_b: float,
    Omega_cdm: float,
    P_k_max_h_Mpc: float,
    A_s: float = 2.1e-9,
    n_s: float = 0.9649,
    z_pk: float = 0.0,
    m_ncdm: float = None,
    N_ncdm: int = None,
    w0_fld: float = None,
) -> str:
    """
    Compute matter power spectrum P(k) for given cosmological parameters using CLASS.

    Args:
        k_values: dataset_name from create_theory_k_grid() (NOT observational k-bins)
        h: Hubble parameter h = H0/100 km/s/Mpc
        Omega_b: Baryon density parameter
        Omega_cdm: Cold dark matter density parameter
        P_k_max_h_Mpc: Maximum k for CLASS computation (h/Mpc). Must be greater than
            max(k_values) for CLASS to compute P(k) at all requested k points.
        A_s: Scalar amplitude of primordial perturbations (default: 2.1e-9)
        n_s: Scalar spectral index (default: 0.9649)
        z_pk: Redshift for power spectrum computation (default: 0.0)
        m_ncdm: Mass of non-cold dark matter (neutrinos) in eV. For multiple species
            with equal mass, this is the mass per species. E.g., for Σmν=0.15 eV with
            3 degenerate species, use m_ncdm=0.05. (default: None, no massive neutrinos)
        N_ncdm: Number of non-cold dark matter (massive neutrino) species. Use with
            m_ncdm to specify massive neutrinos. E.g., N_ncdm=3 for 3 degenerate species.
            (default: None)
        w0_fld: Dark energy equation of state parameter w0. Use w0_fld=-1.0 for ΛCDM,
            w0_fld=-0.9 for quintessence-like, w0_fld=-1.1 for phantom-like. (default: None, uses -1)

    Returns:
        JSON with dataset_name referencing numpy array of P(k) values in (Mpc/h)^3,
        same length as k_values input. Use dataset_name in subsequent tool calls.
    """
    import numpy as np
    from codes.analysis import compute_power_spectrum as compute_pk
    session = get_session()

    try:
        k_data = session.get_dataset(k_values)
    except KeyError:
        return json.dumps({
            "status": "error",
            "error": f"k_values '{k_values}' not found in session.",
            "hint": "Call create_theory_k_grid() first."
        }, indent=2)

    # Validate P_k_max_h_Mpc > max(k_values)
    k_max = float(np.max(k_data))
    if P_k_max_h_Mpc <= k_max:
        return json.dumps({
            "status": "error",
            "error": f"P_k_max_h_Mpc ({P_k_max_h_Mpc}) must be greater than max(k_values) ({k_max}). "
                     f"CLASS cannot compute P(k) for k values beyond P_k_max_h_Mpc."
        }, indent=2)

    # Build params dict from explicit primitives
    params = {
        'output': 'mPk',
        'P_k_max_h/Mpc': P_k_max_h_Mpc,
        'z_pk': z_pk,
        'h': h,
        'Omega_b': Omega_b,
        'Omega_cdm': Omega_cdm,
        'A_s': A_s,
        'n_s': n_s,
    }

    # Add massive neutrino parameters if specified
    if m_ncdm is not None and N_ncdm is not None:
        # For N degenerate species, CLASS expects comma-separated masses
        params['N_ncdm'] = N_ncdm
        params['m_ncdm'] = ','.join([str(m_ncdm)] * N_ncdm)
    elif m_ncdm is not None:
        # Single massive neutrino species
        params['N_ncdm'] = 1
        params['m_ncdm'] = str(m_ncdm)

    # Add dark energy equation of state if specified
    if w0_fld is not None:
        params['Omega_fld'] = 1.0 - Omega_b - Omega_cdm  # Flat universe
        params['w0_fld'] = w0_fld
        params['wa_fld'] = 0.0  # Constant w

    result = compute_pk(params, k_data)
    dataset_name, info = session.store_derived(result, k_values, "power_spectrum")
    return json.dumps({
        "status": "success",
        "datasets": [dataset_name],
        "columns": ["P(k) (Mpc/h)^3"],
        "row_count": info.row_count,
        "usage": "Refer to this dataset by its name in subsequent tools.",
    }, indent=2)

# COMMENTED OUT - uses hidden default models
# @tool
# def compute_all_models(k_values: str, models_name: str = None) -> str:
#     """
#     Compute power spectra for all standard cosmological models.
#
#     Args:
#         k_values: dataset_name from create_theory_k_grid() (NOT observational k-bins)
#         models_name: Optional dataset_name for custom models dict in session.
#             If None (default), uses standard models: 'ΛCDM', 'ΛCDM + Σmν=0.10 eV',
#             'wCDM (w0=-0.9)', 'Thermal WDM', 'CWDM', 'ETHOS IDM–DR', 'IDM–baryon'.
#
#     Returns:
#         JSON with dataset_name referencing dict where:
#             - Keys (str): Model names
#             - Values (numpy array): P(k) values in (Mpc/h)^3
#         Use dataset_name in subsequent tool calls.
#
#     IMPORTANT: For visualization, model name keys MUST be EXACT:
#         'ΛCDM', 'ΛCDM + Σmν=0.10 eV', 'wCDM (w0=-0.9)'
#     """
#     from codes.analysis import compute_all_models as compute_all
#     session = get_session()
#
#     try:
#         k_data = session.get_dataset(k_values)
#     except KeyError:
#         return json.dumps({
#             "status": "error",
#             "error": f"k_values '{k_values}' not found in session.",
#             "hint": "Call create_theory_k_grid() first."
#         }, indent=2)
#
#     models = None
#     if models_name is not None:
#         try:
#             models = session.get_dataset(models_name)
#         except KeyError:
#             return json.dumps({
#                 "status": "error",
#                 "error": f"models '{models_name}' not found in session."
#             }, indent=2)
#
#     result = compute_all(k_data, models)
#     dataset_name, info = session.store_derived(result, k_values, "all_models")
#     return json.dumps({
#         "status": "success",
#         "datasets": [dataset_name],
#         "columns": list(result.keys()),
#         "row_count": info.row_count,
#         "usage": "Refer to this dataset by its name in subsequent tools.",
#     }, indent=2)

@tool
def compute_suppression_ratio(
    reference_pk: str,
    compare_pk: str,
    compare_name: str,
) -> str:
    """
    Compute power spectrum suppression ratio P(k) / P_reference(k).

    Args:
        reference_pk: dataset_name for reference model P(k) array (e.g., ΛCDM)
        compare_pk: dataset_name for model P(k) array to compare
        compare_name: Label for the comparison model (used in output dataset name)

    Returns:
        JSON with dataset_name for suppression ratio array.
        Values < 1.0 indicate suppression, > 1.0 indicate enhancement.
    """
    import numpy as np
    session = get_session()

    P_ref = np.asarray(session.get_dataset(reference_pk), dtype=float)
    P_compare = np.asarray(session.get_dataset(compare_pk), dtype=float)

    ratio = P_compare / P_ref

    # Store with descriptive name
    safe_name = compare_name.replace(' ', '_').replace('/', '_')
    dataset_name, info = session.store_derived(ratio, reference_pk, f"ratio_{safe_name}")

    return json.dumps({
        "status": "success",
        "dataset": dataset_name,
        "model": compare_name,
        "row_count": info.row_count,
    }, indent=2)