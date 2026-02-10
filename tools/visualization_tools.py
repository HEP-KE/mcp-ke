from smolagents import tool
from mcp_utils.session import get_session


@tool
def plot_power_spectra(k_theory: str, model_results: str, k_obs: str, Pk_obs: str, Pk_obs_err: str, save_path: str = None) -> str:
    """
    Create TWO-PANEL plot: power spectra comparison + ratio to ΛCDM.

    Args:
        k_theory: dataset_name from create_theory_k_grid(), referencing numpy array
            with dtype float64 containing k values in h/Mpc for theoretical models
            (typically 300 points)
        model_results: dataset_name from compute_all_models(), referencing dict where:
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
        k_obs: dataset_name from load_observational_data(), referencing numpy array
            with dtype float64 containing k values in h/Mpc for observations (typically 19 points)
        Pk_obs: dataset_name from load_observational_data(), referencing numpy array
            with dtype float64 containing observed P(k) values in (Mpc/h)^3, same length as k_obs
        Pk_obs_err: dataset_name from load_observational_data(), referencing numpy array
            with dtype float64 containing error/uncertainty values in (Mpc/h)^3, same length as k_obs
        save_path: Optional filename (e.g., 'my_plot.png'). If just a filename, saves to 'out/' directory
                  in your current working directory. If an absolute path or contains path separators, uses it as-is.
                  Default: 'power_spectra_comparison.png'

                  IMPORTANT: You must have an 'out/' directory in your working directory.

    Returns:
        str: Absolute path to saved plot PNG file
    """
    import matplotlib.pyplot as plt
    from mcp_utils import get_output_path

    if save_path is not None:
        if not save_path.endswith('.png'):
            save_path = save_path + '.png'
        final_path = get_output_path(save_path)
    else:
        final_path = get_output_path('power_spectra_comparison.png')

    session = get_session()
    k_theory_data = session.get_dataset(k_theory)
    model_results_data = session.get_dataset(model_results)
    k_obs_data = session.get_dataset(k_obs)
    Pk_obs_data = session.get_dataset(Pk_obs)
    Pk_obs_err_data = session.get_dataset(Pk_obs_err)

    from codes.viz import plot_power_spectra as plot_pk
    fig = plot_pk(k_theory_data, model_results_data, k_obs_data, Pk_obs_data, Pk_obs_err_data, final_path)
    plt.close(fig)
    return f"Plot saved to: {final_path}"

@tool
def plot_suppression_ratios(k_values: str, suppression_ratios: str, reference_model: str = 'ΛCDM', save_path: str = None) -> str:
    """
    Plot suppression ratios P(k)/P_reference(k) in standalone single-panel figure.

    Note: plot_power_spectra() already includes suppression in bottom panel.

    Args:
        k_values: dataset_name from create_theory_k_grid(), referencing numpy array
            with dtype float64 containing k values in h/Mpc
            (should match the k-grid used to compute suppression_ratios)
        suppression_ratios: dataset_name from compute_suppression_ratios(), referencing dict where:
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
                same length as k_values
        reference_model: Name of reference model used in plot label (default: 'ΛCDM')
        save_path: Optional filename (e.g., 'my_plot.png'). If just a filename, saves to 'out/' directory
                  in your current working directory. If an absolute path or contains path separators, uses it as-is.
                  Default: 'suppression_ratios.png'

                  IMPORTANT: You must have an 'out/' directory in your working directory.

    Returns:
        str: Absolute path to saved plot PNG file
    """
    import matplotlib.pyplot as plt
    from mcp_utils import get_output_path

    if save_path is not None:
        if not save_path.endswith('.png'):
            save_path = save_path + '.png'
        final_path = get_output_path(save_path)
    else:
        final_path = get_output_path('suppression_ratios.png')

    session = get_session()
    k_data = session.get_dataset(k_values)
    ratios_data = session.get_dataset(suppression_ratios)

    from codes.viz import plot_suppression_ratios as plot_suppression
    fig = plot_suppression(k_data, ratios_data, reference_model, final_path)
    plt.close(fig)
    return f"Plot saved to: {final_path}"