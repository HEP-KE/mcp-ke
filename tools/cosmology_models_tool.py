from smolagents import tool

@tool
def LCDM() -> dict:
    """
    Flat ΛCDM baseline (cold dark matter + cosmological constant).

    The standard 6-parameter cosmological model with cold dark matter and
    cosmological constant dark energy (w = -1).

    Papers:
        - CLASS code: https://arxiv.org/abs/1104.2933
        - Planck 2018 params: https://arxiv.org/abs/1807.06209

    Args: None
    Returns:
        dict for Planck 2018 cosmological parameters with these exact keys:
            'output' (str)
            'P_k_max_h/Mpc' (float)
            'z_pk' (float)
            'h' (float)
            'Omega_b' (float)
            'Omega_cdm' (float)
            'A_s' (float)
            'n_s' (float)
    """
    from .cosmology_models import LCDM as LCDM_model
    return LCDM_model()

@tool
def nu_mass(sum_mnu_eV: float = 0.10, N_species: int = 1) -> dict:
    """
    ΛCDM + massive neutrinos.

    Adds massive neutrinos implemented as non-cold dark matter (ncdm) species.
    Massive neutrinos suppress small-scale power via free-streaming. The total
    neutrino mass is split equally among N_species degenerate mass eigenstates.

    Relevant Papers:
        - Lesgourgues & Pastor review: https://arxiv.org/abs/1212.6154
        - Planck 2018 neutrino constraints: https://arxiv.org/abs/1807.06209

    Args:
        sum_mnu_eV: Total neutrino mass in eV (default: 0.1 eV)
        N_species: Number of massive neutrino species (default: 1)
    
    Returns:
        dict keys:
            'output' (str)
            'P_k_max_h/Mpc' (float)
            'z_pk' (float)
            'h' (float)
            'Omega_b' (float)
            'Omega_cdm' (float)
            'A_s' (float)
            'n_s' (float)
            'N_ur' (float) - number of massless relativistic species
            'N_ncdm' (int) - number of massive neutrino species
            'm_ncdm' (str or float) - neutrino mass(es) in eV
            'T_ncdm' (str or float) - neutrino temperature ratio

    """
    from .cosmology_models import nu_mass as nu_mass_model
    return nu_mass_model(sum_mnu_eV, N_species)

@tool
def wCDM(w0: float = -0.9) -> dict:
    """
    Dark energy with constant equation of state parameter w0.

    Constant dark energy equation of state w = w0 (here w0 ≈ -0.9).
    This alters late-time growth and distance relations compared to ΛCDM (w = -1).

    Papers:
        - Chevallier-Polarski parametrization: https://arxiv.org/abs/gr-qc/0009008
        - Linder review: https://arxiv.org/abs/astro-ph/0208512

    Note: Returns a dict with special 'w0_approx' key for post-processing if CLASS
          doesn't support fluid dark energy.

    Args:
        w0: Dark energy equation of state (default: -0.9)
    
    Returns:
        dict keys:
            'output' (str)
            'P_k_max_h/Mpc' (float)
            'z_pk' (float)
            'h' (float)
            'Omega_b' (float)
            'Omega_cdm' (float)
            'A_s' (float)
            'n_s' (float)
            '_w0_approx' (float) - the w0 value for approximate scaling

    """
    from .cosmology_models import wCDM as wCDM_model
    return wCDM_model(w0)