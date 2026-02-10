import json
from smolagents import tool
from mcp_utils.session import get_session

@tool
def compute_power_spectrum(params: dict, k_values: str) -> str:
    """
    Compute matter power spectrum P(k) for given cosmological parameters using CLASS.

    Args:
        params: Dictionary of CLASS cosmological parameters with required keys:
            - 'output' (str): 'mPk' for matter power spectrum
            - 'P_k_max_h/Mpc' (float): maximum k value for P(k) table
            - 'z_pk' (float): redshift for power spectrum
            - 'h' (float): Hubble parameter H0/100
            - 'Omega_b' (float): physical baryon density ω_b = Ω_b h²
            - 'Omega_cdm' (float): physical CDM density ω_cdm = Ω_cdm h²
            - 'A_s' (float): scalar amplitude of primordial fluctuations
            - 'n_s' (float): scalar spectral index

            Optional model-specific keys (depending on cosmology):
            - 'N_ur' (float): number of massless relativistic species
            - 'N_ncdm' (int): number of massive neutrino species
            - 'm_ncdm' (str or float): neutrino mass(es) in eV
            - 'T_ncdm' (str or float): neutrino temperature ratio
            - '_w0_approx' (float): dark energy equation of state parameter

        k_values: dataset_name from create_theory_k_grid() (NOT observational k-bins)

    Returns:
        JSON with dataset_name referencing numpy array of P(k) values in (Mpc/h)^3,
        same length as k_values input. Use dataset_name in subsequent tool calls.
    """
    from codes.analysis import compute_power_spectrum as compute_pk
    session = get_session()
    k_data = session.get_dataset(k_values)
    result = compute_pk(params, k_data)
    dataset_name, info = session.store_derived(result, k_values, "power_spectrum")
    return json.dumps({"dataset_name": dataset_name, "row_count": info.row_count}, indent=2)

@tool
def compute_all_models(k_values: str, models: dict = None) -> str:
    """
    Compute power spectra for all standard cosmological models.

    Args:
        k_values: dataset_name from create_theory_k_grid() (NOT observational k-bins)
        models: Optional dictionary of models where:
            - Keys (str): Model names like 'ΛCDM', 'ΛCDM + Σmν=0.10 eV', 'wCDM (w0=-0.9)'
            - Values (dict): Parameter dictionaries with same structure as compute_power_spectrum params argument
            If None, uses default standard models: 'ΛCDM', 'ΛCDM + Σmν=0.10 eV', 'wCDM (w0=-0.9)',
            'Thermal WDM (all DM, m=3 keV)', 'CWDM (f_wdm=0.2, m=3 keV, g*=100)', 'ETHOS IDM–DR (fiducial)',
            'IDM–baryon (σ=1e-41 cm², n=-4)'

    Returns:
        JSON with dataset_name referencing dict where:
            - Keys (str): Model names. If models=None, returns these exact keys:
                'ΛCDM', 'ΛCDM + Σmν=0.10 eV', 'wCDM (w0=-0.9)',
                'Thermal WDM (all DM, m=3 keV)', 'CWDM (f_wdm=0.2, m=3 keV, g*=100)',
                'ETHOS IDM–DR (fiducial)', 'IDM–baryon (σ=1e-41 cm², n=-4)'
            - Values (numpy array): P(k) values in (Mpc/h)^3, dtype float64
        Use dataset_name in subsequent tool calls.

    IMPORTANT: For visualization, model name keys MUST be EXACT:
        'ΛCDM', 'ΛCDM + Σmν=0.10 eV', 'wCDM (w0=-0.9)'
    """
    from codes.analysis import compute_all_models as compute_all
    session = get_session()
    k_data = session.get_dataset(k_values)
    result = compute_all(k_data, models)
    dataset_name, info = session.store_derived(result, k_values, "all_models")
    return json.dumps({"dataset_name": dataset_name, "models": list(result.keys())}, indent=2)

@tool
def compute_suppression_ratios(model_results: str, k_values: str, reference_model: str = 'ΛCDM') -> str:
    """
    Compute power spectrum suppression ratios P(k) / P_reference(k) for all models.

    Args:
        model_results: dataset_name from compute_all_models(), referencing dict where:
            - Keys (str): Model names like 'ΛCDM', 'ΛCDM + Σmν=0.10 eV', 'wCDM (w0=-0.9)'
            - Values (numpy array): P(k) arrays with dtype float64 in (Mpc/h)^3
        k_values: dataset_name from create_theory_k_grid(), referencing numpy array
            with dtype float64 containing k values in h/Mpc
            (should match the k-grid used to compute model_results)
        reference_model: Name of the reference model (default: 'ΛCDM').
            This MUST be one of the keys in model_results dict.

    Returns:
        JSON with dataset_name referencing dict where:
            - Keys (str): Model names from model_results, EXCLUDING the reference_model itself
                Example: if model_results has keys ['ΛCDM', 'ΛCDM + Σmν=0.10 eV', 'wCDM (w0=-0.9)']
                and reference_model='ΛCDM', returns keys ['ΛCDM + Σmν=0.10 eV', 'wCDM (w0=-0.9)']
            - Values (numpy array): Dimensionless suppression ratios P(k)/P_reference(k),
                dtype float64, same length as k_values input
                Values < 1.0 indicate suppression relative to reference model
                Values > 1.0 indicate enhancement relative to reference model
        Use dataset_name in subsequent tool calls.
    """
    from codes.analysis import compute_suppression_ratios as compute_suppression
    session = get_session()
    model_data = session.get_dataset(model_results)
    k_data = session.get_dataset(k_values)
    result = compute_suppression(model_data, k_data, reference_model)
    dataset_name, info = session.store_derived(result, model_results, "suppression_ratios")
    return json.dumps({"dataset_name": dataset_name, "models": list(result.keys())}, indent=2)