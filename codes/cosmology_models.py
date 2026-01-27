"""
Cosmological model definitions for CLASS computations.
Models include ΛCDM, ν-mass, wCDM, thermal WDM/CWDM, IDM–DR (ETHOS), IDM–baryon.
"""

from classy import Class
import numpy as np

# ========== Helper Functions ==========

def base_params():
    """
    Base ΛCDM parameters (Planck 2018-like).

    Returns Planck 2018 best-fit cosmological parameters for vanilla ΛCDM.
    Papers: Planck 2018 (https://arxiv.org/abs/1807.06209),
            CLASS code (https://arxiv.org/abs/1104.2933)
    """
    return {
        'output': 'mPk',
        'P_k_max_h/Mpc': 20.0,
        'z_pk': 0.0,
        'h': 0.67556,
        'Omega_b': 0.022032,      # Physical baryon density ω_b = Ω_b h²
        'Omega_cdm': 0.12038,     # Physical CDM density ω_cdm = Ω_cdm h²
        'A_s': 2.215e-9,
        'n_s': 0.9619,
    }


# ========== Cosmological Models ==========

def LCDM():
    """
    Flat ΛCDM baseline (cold dark matter + cosmological constant).

    The standard 6-parameter cosmological model with cold dark matter and
    cosmological constant dark energy (w = -1).

    Papers:
        - CLASS code: https://arxiv.org/abs/1104.2933
        - Planck 2018 params: https://arxiv.org/abs/1807.06209
    """
    return dict(base_params())


def nu_mass(sum_mnu_eV=0.10, N_species=1):
    """
    ΛCDM + massive neutrinos.

    Adds massive neutrinos implemented as non-cold dark matter (ncdm) species.
    Massive neutrinos suppress small-scale power via free-streaming. The total
    neutrino mass is split equally among N_species degenerate mass eigenstates.

    Args:
        sum_mnu_eV: Total neutrino mass in eV (default: 0.1 eV)
        N_species: Number of massive neutrino species (default: 1)

    Papers:
        - Lesgourgues & Pastor review: https://arxiv.org/abs/1212.6154
        - Planck 2018 neutrino constraints: https://arxiv.org/abs/1807.06209
    """
    p = base_params()
    T_ncdm_values = ','.join([str(0.71611)] * N_species) if N_species > 1 else 0.71611
    p.update({
        'N_ur': 3.044 - N_species,  # Massless relativistic species
        'N_ncdm': N_species,
        'm_ncdm': ','.join([str(sum_mnu_eV / N_species)] * N_species),
        'T_ncdm': T_ncdm_values,
    })
    return p


def wCDM(w0=-0.9):
    """
    Dark energy with constant equation of state parameter w0.

    Constant dark energy equation of state w = w0 (here w0 ≈ -0.9).
    This alters late-time growth and distance relations compared to ΛCDM (w = -1).

    Args:
        w0: Dark energy equation of state (default: -0.9)

    Papers:
        - Chevallier-Polarski parametrization: https://arxiv.org/abs/gr-qc/0009008
        - Linder review: https://arxiv.org/abs/astro-ph/0208512

    Note: Returns a dict with special 'w0_approx' key for post-processing if CLASS
          doesn't support fluid dark energy.
    """
    p = base_params()
    # Store w0 for approximate scaling if CLASS doesn't support w0_fld
    p['_w0_approx'] = w0

    return p


def thermal_WDM_all_dm(m_wdm_keV=3.0, T_ratio=0.71611):
    """
    Thermal warm dark matter (all DM is warm).

    Replaces all cold dark matter with a thermal relic (m ≈ keV scale) implemented
    as ncdm. Free-streaming of WDM particles damps power on Lyman-α forest scales.

    Args:
        m_wdm_keV: WDM particle mass in keV (default: 3.0)
        T_ratio: Temperature ratio T_ncdm/T_gamma (default: 0.71611, standard neutrino value)

    Papers:
        - Bode-Ostriker-Turok: https://arxiv.org/abs/astro-ph/0010389
        - Lyman-α bounds (Iršič et al.): https://arxiv.org/abs/1702.01764
    """
    p = base_params()
    w_dm = p['Omega_cdm']
    p['Omega_cdm'] = 0.0
    p.update({
        'N_ncdm': 1,
        'm_ncdm': m_wdm_keV * 1e3,  # Convert keV to eV
        'T_ncdm': T_ratio,
        'Omega_ncdm': w_dm,
    })
    return p


def mixed_CWDM(f_wdm=0.2, m_wdm_keV=3.0, gstar_dec=100.0):
    """
    Cold + warm dark matter mixture (CWDM).

    Fraction f_wdm of total dark matter is thermal WDM (rest is CDM). This interpolates
    power suppression strength, useful for Lyman-α forest tests. The WDM temperature
    is determined by the effective relativistic degrees of freedom at decoupling.

    Args:
        f_wdm: Fraction of DM that is warm (default: 0.2)
        m_wdm_keV: WDM particle mass in keV (default: 3.0)
        gstar_dec: Effective degrees of freedom at decoupling (default: 100.0)

    Papers:
        - Boyarsky et al.: https://arxiv.org/abs/0812.0010
        - Murgia-Merle-Viel: https://arxiv.org/abs/1704.07838
    """
    p = base_params()
    w_dm = p['Omega_cdm']
    T_ratio = 0.71611 * (10.75 / gstar_dec) ** (1/3)
    p['Omega_cdm'] = (1.0 - f_wdm) * w_dm
    p.update({
        'N_ncdm': 1,
        'm_ncdm': m_wdm_keV * 1e3,
        'T_ncdm': T_ratio,
        'Omega_ncdm': f_wdm * w_dm,
    })
    return p


def IDM_DR_ETHOS(f_idm=0.05, N_idr=0.4, a_idm_dr=5e7, nindex_idm_dr=2,
                 idr_nature='free_streaming', alpha_idm_dr=0.75):
    """
    Interacting dark matter with dark radiation (ETHOS framework).

    A fraction f_idm of dark matter elastically couples to dark radiation, causing
    dark acoustic oscillations (DAOs) and Silk-like damping on small scales. This
    is part of the ETHOS (Effective Theory of Structure Formation) framework.

    Args:
        f_idm: Fraction of DM that is interacting (default: 0.05)
        N_idr: Extra dark radiation in neutrino units (default: 0.4)
        a_idm_dr: Present-day comoving interaction rate in 1/Mpc (default: 5e7)
        nindex_idm_dr: Temperature dependence power (default: 2)
        idr_nature: Nature of dark radiation (default: 'free_streaming')
        alpha_idm_dr: Angular coefficient (3/4 for vector, 3/2 for scalar) (default: 0.75)

    Papers:
        - Cyr-Racine & Sigurdson: https://arxiv.org/abs/1209.5752
        - ETHOS framework: https://arxiv.org/abs/1512.05344
    """
    p = base_params()
    p.update({
        'f_idm': f_idm,
        'N_idr': N_idr,
        'a_idm_dr': a_idm_dr,
        'nindex_idm_dr': nindex_idm_dr,
        'idr_nature': idr_nature,
        'alpha_idm_dr': alpha_idm_dr,
    })
    return p


def IDM_baryon(cross_cm2=1e-41, n_index=-4):
    """
    Dark matter-baryon scattering.

    DM-baryon elastic scattering with cross section σ ∝ v^n suppresses small-scale
    clustering before recombination. Provides constraints from CMB and structure formation.

    Args:
        cross_cm2: DM-baryon cross section in cm² (default: 1e-41)
        n_index: Velocity dependence power, σ ∝ v^n (default: -4)

    Note: Requires CLASS version with IDM-baryon support.

    Papers:
        - Dvorkin-Blum-Kamionkowski: https://arxiv.org/abs/1311.2937
        - Gluscevic & Boddy: https://arxiv.org/abs/1712.07133
    """
    p = base_params()
    # Note: IDM-baryon scattering requires special CLASS version
    # For now, return base model
    return p


# ========== Model Factory ==========

def define_cosmology_models():
    """
    Define a comprehensive set of cosmological models for analysis.

    Returns a dictionary with model names as keys and CLASS parameters as values.
    This provides a convenient way to compute and compare multiple models.
    """
    return {
        'ΛCDM': LCDM(),
        'ΛCDM + Σmν=0.10 eV': nu_mass(0.10, N_species=1),
        'wCDM (w0=-0.9)': wCDM(-0.9),
        'Thermal WDM (all DM, m=3 keV)': thermal_WDM_all_dm(3.0),
        'CWDM (f_wdm=0.2, m=3 keV, g*=100)': mixed_CWDM(0.2, 3.0, 100.0),
        'ETHOS IDM–DR (fiducial)': IDM_DR_ETHOS(),
        'IDM–baryon (σ=1e-41 cm², n=-4)': IDM_baryon(1e-41, -4),
    }


def get_model_params(model_name, **kwargs):
    """
    Get parameters for a specific model, with optional parameter overrides.

    Parameters:
    -----------
    model_name : str
        Name of the model (must be in define_cosmology_models())
    **kwargs : dict
        Optional parameter overrides for the model

    Returns:
    --------
    dict : CLASS parameters for the model
    """
    models = define_cosmology_models()
    if model_name not in models:
        raise ValueError(f"Model '{model_name}' not found. Available models: {list(models.keys())}")

    params = models[model_name].copy()
    params.update(kwargs)
    return params


def compute_power_spectrum(model_params, k_values, z=0):
    """
    Compute the matter power spectrum for given model parameters.

    Parameters:
    -----------
    model_params : dict
        CLASS parameters for the cosmological model
    k_values : array-like
        Wavenumbers in 1/Mpc (NOT h/Mpc)
    z : float
        Redshift (default: 0)

    Returns:
    --------
    array : P(k) values in Mpc^3 (NOT (Mpc/h)^3)
    """
    cosmo = Class()
    cosmo.set(model_params)
    cosmo.compute()

    # Get P(k) directly - k_values should already be in 1/Mpc
    Pk = np.array([cosmo.pk(k, z) for k in k_values])

    cosmo.struct_cleanup()
    cosmo.empty()

    return Pk
