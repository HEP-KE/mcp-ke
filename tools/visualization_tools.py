from smolagents import tool

@tool
def plot_power_spectra(k_theory: object, model_results: dict, k_obs: object, Pk_obs: object, σPk_obs: object, save_path: str = None) -> str:
    """
    Create TWO-PANEL plot: power spectra comparison + ratio to ΛCDM.

    Args:
        k_theory: Numpy array with dtype float64 containing k values in h/Mpc for theoretical models
            (typically 300 points from create_theory_k_grid())
        model_results: Dictionary where:
            - Keys (str): Model names. To get predefined colors/linestyles, use EXACT names:
                'ΛCDM' (black, solid)
                'ΛCDM + Σmν=0.06 eV' (cyan, dashed)
                'ΛCDM + Σmν=0.10 eV' (blue, dashed)
                'wCDM (w0=-0.9)' (red, dash-dot)
                'wCDM (w0=-1.1)' (darkred, dash-dot)
                'Thermal WDM (all DM, m=3 keV)' (green, dotted)
                'CWDM (f_wdm=0.2, m=3 keV, g*=100)' (orange, dashed)
                'ETHOS IDM–DR (fiducial)' (purple, dash-dot)
                'IDM–baryon (σ=1e-41 cm², n=-4)' (brown, dotted)
                Any other names will be plotted in gray with solid line.
            - Values (numpy array): P(k) arrays with dtype float64 in (Mpc/h)^3, same length as k_theory
            This is typically the output from compute_all_models()
        k_obs: Numpy array with dtype float64 containing k values in h/Mpc for observations
            (typically 19 points from observational data)
        Pk_obs: Numpy array with dtype float64 containing observed P(k) values in (Mpc/h)^3, same length as k_obs
        σPk_obs: Numpy array with dtype float64 containing error/uncertainty values in (Mpc/h)^3, same length as k_obs
        save_path: Optional filename (e.g., 'my_plot.png'). If just a filename, saves to 'out/' directory
                  in your current working directory. If an absolute path or contains path separators, uses it as-is.
                  Default: 'power_spectra_comparison.png'

                  IMPORTANT: You must have an 'out/' directory in your working directory.

    Returns:
        str: Absolute path to saved plot PNG file
    """
    from mcp_utils import get_output_path

    if save_path is not None:
        # Ensure .png extension
        if not save_path.endswith('.png'):
            save_path = save_path + '.png'
        # Get output path (handles output/ directory logic)
        final_path = get_output_path(save_path)
    else:
        # Default filename
        final_path = get_output_path('power_spectra_comparison.png')

    from .viz import plot_power_spectra as plot_pk
    return plot_pk(k_theory, model_results, k_obs, Pk_obs, σPk_obs, final_path)

@tool
def plot_suppression_ratios(k_values: object, suppression_ratios: dict, reference_model: str = 'ΛCDM', save_path: str = None) -> str:
    """
    Plot suppression ratios P(k)/P_reference(k) in standalone single-panel figure.

    Note: plot_power_spectra() already includes suppression in bottom panel.

    Args:
        k_values: Numpy array with dtype float64 containing k values in h/Mpc
            (should match the k-grid used to compute suppression_ratios)
        suppression_ratios: Dictionary where:
            - Keys (str): Model names (excludes the reference model). To get predefined colors, use EXACT names:
                'ΛCDM + Σmν=0.06 eV' (cyan)
                'ΛCDM + Σmν=0.10 eV' (blue)
                'wCDM (w0=-0.9)' (red)
                'wCDM (w0=-1.1)' (darkred)
                'Thermal WDM (all DM, m=3 keV)' (green)
                'CWDM (f_wdm=0.2, m=3 keV, g*=100)' (orange)
                'ETHOS IDM–DR (fiducial)' (purple)
                'IDM–baryon (σ=1e-41 cm², n=-4)' (brown)
                Any other names will be plotted in gray.
            - Values (numpy array): Dimensionless suppression ratios P(k)/P_reference(k) with dtype float64,
                same length as k_values. This is typically the output from compute_suppression_ratios()
        reference_model: Name of reference model used in plot label (default: 'ΛCDM')
        save_path: Optional filename (e.g., 'my_plot.png'). If just a filename, saves to 'out/' directory
                  in your current working directory. If an absolute path or contains path separators, uses it as-is.
                  Default: 'suppression_ratios.png'

                  IMPORTANT: You must have an 'out/' directory in your working directory.

    Returns:
        str: Absolute path to saved plot PNG file
    """
    from mcp_utils import get_output_path

    if save_path is not None:
        # Ensure .png extension
        if not save_path.endswith('.png'):
            save_path = save_path + '.png'
        # Get output path (handles output/ directory logic)
        final_path = get_output_path(save_path)
    else:
        # Default filename
        final_path = get_output_path('suppression_ratios.png')

    from .viz import plot_suppression_ratios as plot_suppression
    return plot_suppression(k_values, suppression_ratios, reference_model, final_path)