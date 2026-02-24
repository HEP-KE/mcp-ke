import json
from smolagents import tool
from mcp_utils.session import get_session


@tool
def plot_power_spectra(
    k_theory: str,
    k_obs: str,
    Pk_obs: str,
    Pk_obs_err: str,
    # Model 1 (required)
    model1_pk: str,
    model1_name: str,
    # Models 2-5 (optional)
    model2_pk: str = None,
    model2_name: str = None,
    model3_pk: str = None,
    model3_name: str = None,
    model4_pk: str = None,
    model4_name: str = None,
    model5_pk: str = None,
    model5_name: str = None,
    save_path: str = None
) -> str:
    """
    Create TWO-PANEL plot: power spectra comparison + ratio to first model.

    Args:
        k_theory: dataset_name for k values array (h/Mpc) for theoretical models
        k_obs: dataset_name for observed k values array (h/Mpc)
        Pk_obs: dataset_name for observed P(k) values array (Mpc/h)^3
        Pk_obs_err: dataset_name for P(k) error values array (Mpc/h)^3
        model1_pk: dataset_name for first model P(k) array (used as reference in ratio panel)
        model1_name: Label for first model (e.g., 'ΛCDM')
        model2_pk: dataset_name for second model P(k) array (optional)
        model2_name: Label for second model (optional)
        model3_pk: dataset_name for third model P(k) array (optional)
        model3_name: Label for third model (optional)
        model4_pk: dataset_name for fourth model P(k) array (optional)
        model4_name: Label for fourth model (optional)
        model5_pk: dataset_name for fifth model P(k) array (optional)
        model5_name: Label for fifth model (optional)
        save_path: Output filename (default: 'power_spectra_comparison.png')

    Returns:
        JSON with path to saved plot PNG file
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
    k_obs_data = session.get_dataset(k_obs)
    Pk_obs_data = session.get_dataset(Pk_obs)
    Pk_obs_err_data = session.get_dataset(Pk_obs_err)

    # Build model_results dict from individual datasets
    model_results_data = {}
    for pk_name, label in [
        (model1_pk, model1_name),
        (model2_pk, model2_name),
        (model3_pk, model3_name),
        (model4_pk, model4_name),
        (model5_pk, model5_name),
    ]:
        if pk_name is not None and label is not None:
            model_results_data[label] = session.get_dataset(pk_name)

    from codes.viz import plot_power_spectra as plot_pk
    fig = plot_pk(k_theory_data, model_results_data, k_obs_data, Pk_obs_data, Pk_obs_err_data, final_path)
    plt.close(fig)
    return json.dumps({
        "status": "success",
        "file": final_path,
        "type": "plot",
        "description": f"Two-panel power spectra comparison with {len(model_results_data)} models",
    }, indent=2)

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
    return json.dumps({
        "status": "success",
        "file": final_path,
        "type": "plot",
        "description": f"Suppression ratios P(k)/P_{reference_model}(k)",
    }, indent=2)