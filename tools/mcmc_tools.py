"""
MCP tool wrappers for MCMC Bayesian inference.

Provides tools for running MCMC parameter estimation, creating diagnostic plots,
and analyzing posterior distributions for cosmological models.
"""

from smolagents import tool
from typing import List, Dict, Optional
import json
from mcp_utils.session import get_session


# =============================================================================
# WRAPPER DESIGN NOTE:
#
# Parameter bounds (for VARIED params) are passed via DataFrame in session.
# Fixed cosmological parameters are explicit primitives in run_mcmc_cosmology.
#
# The domain scientist's codes/mcmc.py handles mapping to CLASS inputs via
# map_params_to_class() - supports both direct CLASS params (h, Omega_cdm, etc.)
# and derived aliases (Omega_m, sigma8, sum_mnu) that get converted internally.
# =============================================================================


@tool
def set_mcmc_param_bounds(
    param1_name: str,
    param1_min: float,
    param1_max: float,
    param2_name: str = None,
    param2_min: float = None,
    param2_max: float = None,
    param3_name: str = None,
    param3_min: float = None,
    param3_max: float = None,
    param4_name: str = None,
    param4_min: float = None,
    param4_max: float = None,
    param5_name: str = None,
    param5_min: float = None,
    param5_max: float = None,
    param6_name: str = None,
    param6_min: float = None,
    param6_max: float = None,
) -> str:
    """
    Set MCMC parameter bounds and store as DataFrame in session.

    Defines which cosmological parameters to vary and their prior bounds.
    Stores as DataFrame with columns [name, min, max] for use by run_mcmc_cosmology.
    Parameters are mapped to CLASS inputs by the domain scientist code.

    Args:
        param1_name: First parameter name (required). CLASS params: h, Omega_cdm,
            Omega_b, A_s, n_s, tau_reio, w0_fld, wa_fld, m_ncdm, N_ur, Omega_k.
            Derived aliases: Omega_m, sigma8, sum_mnu, N_eff.
        param1_min: Minimum bound for first parameter (required)
        param1_max: Maximum bound for first parameter (required)
        param2_name: Second parameter name (optional)
        param2_min: Minimum bound for second parameter
        param2_max: Maximum bound for second parameter
        param3_name: Third parameter name (optional)
        param3_min: Minimum bound for third parameter
        param3_max: Maximum bound for third parameter
        param4_name: Fourth parameter name (optional)
        param4_min: Minimum bound for fourth parameter
        param4_max: Maximum bound for fourth parameter
        param5_name: Fifth parameter name (optional)
        param5_min: Minimum bound for fifth parameter
        param5_max: Maximum bound for fifth parameter
        param6_name: Sixth parameter name (optional)
        param6_min: Minimum bound for sixth parameter
        param6_max: Maximum bound for sixth parameter

    Returns:
        JSON with dataset name for the stored parameter bounds DataFrame.
    """
    import pandas as pd
    from codes.mcmc import KNOWN_CLASS_PARAMS, DERIVED_PARAM_NAMES

    # Build list of param bounds from provided values
    params = []
    for i, (name, pmin, pmax) in enumerate([
        (param1_name, param1_min, param1_max),
        (param2_name, param2_min, param2_max),
        (param3_name, param3_min, param3_max),
        (param4_name, param4_min, param4_max),
        (param5_name, param5_min, param5_max),
        (param6_name, param6_min, param6_max),
    ], start=1):
        if name is not None:
            if pmin is None or pmax is None:
                return f"Error: param{i}_name is set but param{i}_min or param{i}_max is missing"
            if pmin >= pmax:
                return f"Error: param{i}_min ({pmin}) must be less than param{i}_max ({pmax})"
            # Validate parameter name against known CLASS params
            all_valid = KNOWN_CLASS_PARAMS | DERIVED_PARAM_NAMES
            if name not in all_valid:
                return f"Error: Unknown parameter '{name}'. Must be CLASS param or derived alias."
            params.append({'name': name, 'min': pmin, 'max': pmax})

    if not params:
        return "Error: At least one parameter must be specified"

    # Store as DataFrame in session
    df = pd.DataFrame(params)
    session = get_session()
    dataset_name, info = session.load_dataset(df, name='mcmc_param_bounds')

    return json.dumps({
        "status": "success",
        "dataset": {
            "name": dataset_name,
            "type": "DataFrame",
            "rows": info.row_count,
            "columns": info.columns
        },
        "parameters": [p['name'] for p in params],
        "notes": f"Use '{dataset_name}' as param_bounds_name in run_mcmc_cosmology."
    }, indent=2)


@tool
def run_mcmc_cosmology(
    k_obs: str,
    Pk_obs: str,
    Pk_obs_err: str,
    P_k_max_h_Mpc: float,
    param_bounds_name: str = "mcmc_param_bounds",
    # Fixed cosmological parameters (explicit, no hidden defaults)
    h: float = 0.6736,
    Omega_b: float = 0.0493,
    Omega_cdm: float = 0.264,
    A_s: float = 2.1e-9,
    n_s: float = 0.9649,
    z_pk: float = 0.0,
    # MCMC configuration
    nwalkers: int = 32,
    nburn: int = 100,
    nrun: int = 500,
    prior_type: str = 'uniform'
) -> str:
    """
    Run MCMC parameter estimation for cosmological power spectrum fitting.

    Uses emcee (affine-invariant MCMC) to find the posterior distribution
    of cosmological parameters. Parameter bounds must be set first using
    set_mcmc_param_bounds. Parameters are mapped to CLASS inputs internally.

    Args:
        k_obs: dataset_name for observed k values array (h/Mpc)
        Pk_obs: dataset_name for observed P(k) values array (Mpc/h)^3
        Pk_obs_err: dataset_name for P(k) uncertainties array (Mpc/h)^3
        P_k_max_h_Mpc: Maximum k for CLASS computation (h/Mpc). Must be greater than
            max(k_obs) for CLASS to compute P(k) at all observed k points.
        param_bounds_name: dataset_name for parameter bounds DataFrame
            (default: 'mcmc_param_bounds' from set_mcmc_param_bounds)
        h: Hubble parameter h = H0/100 km/s/Mpc (default: 0.6736)
        Omega_b: Baryon density parameter (default: 0.0493)
        Omega_cdm: Cold dark matter density parameter (default: 0.264)
        A_s: Scalar amplitude of primordial perturbations (default: 2.1e-9)
        n_s: Scalar spectral index (default: 0.9649)
        z_pk: Redshift for power spectrum computation (default: 0.0)
        nwalkers: Number of MCMC walkers (default: 32)
        nburn: Number of burn-in steps to discard (default: 100)
        nrun: Number of production run steps (default: 500)
        prior_type: Prior type - 'uniform' or 'gaussian' (default: 'uniform')

    Returns:
        JSON with MCMC results and dataset names for samples DataFrame and base_params.

    Note:
        Parameters being varied (from param_bounds) will override the fixed values
        during sampling. Provide fixed values for parameters NOT being varied.
    """
    from codes.mcmc import (
        run_mcmc, extract_mcmc_results, format_mcmc_summary
    )
    import numpy as np
    import pandas as pd

    session = get_session()

    # Load param_bounds DataFrame from session
    try:
        bounds_df = session.get_dataset(param_bounds_name)
        param_bounds = bounds_df.to_dict('records')  # Convert to list of dicts
    except KeyError:
        return f"Error: Parameter bounds '{param_bounds_name}' not found. Call set_mcmc_param_bounds first."

    # Get observational data from session
    try:
        k_obs_data = session.get_dataset(k_obs)
        Pk_obs_data = session.get_dataset(Pk_obs)
        Pk_obs_err_data = session.get_dataset(Pk_obs_err)
    except KeyError as e:
        return f"Error loading observational data: {str(e)}"

    # Validate P_k_max_h_Mpc > max(k_obs)
    k_max = float(np.max(k_obs_data))
    if P_k_max_h_Mpc <= k_max:
        return json.dumps({
            "status": "error",
            "error": f"P_k_max_h_Mpc ({P_k_max_h_Mpc}) must be greater than max(k_obs) ({k_max}). "
                     f"CLASS cannot compute P(k) for k values beyond P_k_max_h_Mpc."
        }, indent=2)

    # Build base_params dict from explicit primitives
    base_params = {
        'output': 'mPk',
        'P_k_max_h/Mpc': P_k_max_h_Mpc,
        'z_pk': z_pk,
        'h': h,
        'Omega_b': Omega_b,
        'Omega_cdm': Omega_cdm,
        'A_s': A_s,
        'n_s': n_s,
    }

    # Extract names of varied parameters
    param_names = [pb['name'] for pb in param_bounds]

    # Run MCMC (domain scientist code handles CLASS parameter mapping internally)
    try:
        mcmc_result = run_mcmc(
            param_bounds=param_bounds,
            base_params=base_params,
            k_obs=k_obs_data,
            Pk_obs=Pk_obs_data,
            Pk_obs_err=Pk_obs_err_data,
            nwalkers=nwalkers,
            nburn=nburn,
            nrun=nrun,
            prior_type=prior_type,
            progress=False
        )
    except Exception as e:
        return f"Error running MCMC: {str(e)}"

    # Extract results
    samples = mcmc_result['samples']
    results = extract_mcmc_results(samples, param_names)

    # Store samples as pandas DataFrame in session (columns = param names)
    samples_df = pd.DataFrame(samples, columns=param_names)
    samples_name, samples_info = session.load_dataset(samples_df, name='mcmc_samples')

    # Format summary
    summary = format_mcmc_summary(
        results, param_names,
        mcmc_result['acceptance_fraction'],
        nwalkers, nburn, nrun
    )

    return json.dumps({
        "status": "success",
        "summary": summary,
        "datasets": {
            "samples": {
                "name": samples_name,
                "type": "DataFrame",
                "rows": samples_info.row_count,
                "columns": samples_info.columns
            }
        },
        "notes": f"Samples '{samples_name}' stored in session. Use with analyze_mcmc_samples, create_mcmc_corner_plot, create_mcmc_trace_plot, compute_best_fit_power_spectrum."
    }, indent=2)


@tool
def create_mcmc_corner_plot(
    samples: str,
    title: str = None,
    smooth_scale: float = 1.0,
    output_filename: str = None
) -> str:
    """
    Create corner plot (triangle plot) from MCMC samples showing parameter posteriors.

    Generates publication-quality corner plots visualizing posterior distributions
    and correlations between parameters using GetDist for kernel density estimation.

    Args:
        samples: dataset_name for MCMC samples DataFrame stored in session
        title: Optional title for the plot
        smooth_scale: Smoothing scale for KDE (default: 1.0, larger = smoother)
        output_filename: Output filename for the plot (default: auto-generated)

    Returns:
        str: Summary with plot file path and parameter statistics
    """
    from mcp_utils import get_output_path
    from codes.mcmc import create_corner_plot, extract_mcmc_results
    from datetime import datetime
    import random

    # Load DataFrame from session
    session = get_session()
    samples_df = session.get_dataset(samples)
    samples_array = samples_df.values
    param_names = samples_df.columns.tolist()

    n_samples, n_params = samples_array.shape

    # Determine output path
    if output_filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        process_id = random.randint(10000, 99999)
        output_filename = f"mcmc_corner_{timestamp}_pid{process_id}.png"

    if not output_filename.endswith('.png'):
        output_filename = output_filename + '.png'

    output_path = get_output_path(output_filename)

    # Create corner plot (uses column names from DataFrame as labels)
    try:
        plot_path = create_corner_plot(
            samples_array, param_names,
            param_labels=None,
            param_ranges=None,
            title=title,
            smooth_scale=smooth_scale,
            output_path=output_path
        )
    except Exception as e:
        return f"Error creating corner plot: {str(e)}"

    # Compute statistics
    results = extract_mcmc_results(samples_array, param_names)

    summary_lines = [
        "MCMC Corner Plot Created",
        "=" * 40,
        "",
        f"Dataset: {samples}",
        f"Number of samples: {n_samples:,}",
        f"Number of parameters: {n_params}",
        f"Parameters: {', '.join(param_names)}",
        "",
        f"Plot saved to: {plot_path}",
        "",
        "Parameter Statistics (68% credible intervals):",
        "-" * 40,
    ]

    for name in param_names:
        r = results[name]
        summary_lines.append(
            f"  {name}: {r['median']:.6f} +{r['upper_err']:.6f} -{r['lower_err']:.6f}"
        )

    return "\n".join(summary_lines)


@tool
def create_mcmc_trace_plot(
    samples: str,
    max_samples: int = 5000,
    output_filename: str = None
) -> str:
    """
    Create trace plots showing MCMC chain evolution for diagnosing convergence.

    Trace plots show parameter values across iterations, useful for checking:
    - Chain mixing (should look like random noise around a mean)
    - Burn-in identification (initial transient behavior)
    - Convergence issues (trends, stuck chains, multimodality)

    Args:
        samples: dataset_name for MCMC samples DataFrame stored in session
        max_samples: Maximum number of samples to plot for performance (default: 5000)
        output_filename: Output filename for the plot (default: auto-generated)

    Returns:
        str: Summary with plot file path and convergence guidance
    """
    from mcp_utils import get_output_path
    from codes.mcmc import create_trace_plot
    from datetime import datetime
    import random

    # Load DataFrame from session
    session = get_session()
    samples_df = session.get_dataset(samples)
    samples_array = samples_df.values
    param_names = samples_df.columns.tolist()

    n_samples, n_params = samples_array.shape

    # Determine output path
    if output_filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        process_id = random.randint(10000, 99999)
        output_filename = f"mcmc_trace_{timestamp}_pid{process_id}.png"

    if not output_filename.endswith('.png'):
        output_filename = output_filename + '.png'

    output_path = get_output_path(output_filename)

    # Create trace plot (uses column names from DataFrame as labels)
    try:
        plot_path = create_trace_plot(
            samples_array, param_names,
            param_labels=None,
            output_path=output_path,
            max_samples=max_samples
        )
    except Exception as e:
        return f"Error creating trace plot: {str(e)}"

    samples_plotted = min(n_samples, max_samples)

    summary = f"""MCMC Trace Plot Created
========================================

Dataset: {samples}
Total samples: {n_samples:,}
Samples plotted: {samples_plotted:,}
Parameters: {', '.join(param_names)}

Plot saved to: {plot_path}

Interpretation Guide:
- Well-mixed chains: Random fluctuations around a stable mean
- Burn-in visible: Initial systematic drift before stabilizing
- Convergence issues: Trends, periodic patterns, or stuck values
- Multiple modes: Chains jumping between distinct value ranges

Next Steps:
- If chains show trends, consider running longer
- For well-mixed chains, proceed with posterior analysis
- Create corner plots to visualize parameter correlations
"""

    return summary


@tool
def analyze_mcmc_samples(
    samples: str
) -> str:
    """
    Analyze MCMC samples and compute parameter statistics.

    Computes summary statistics including mean, median, standard deviation,
    and credible intervals for all sampled parameters.

    Args:
        samples: dataset_name for MCMC samples DataFrame stored in session

    Returns:
        str: Detailed statistics for each parameter
    """
    import numpy as np

    percentiles = [5, 16, 50, 84, 95]

    # Load DataFrame from session
    session = get_session()
    samples_df = session.get_dataset(samples)
    samples_array = samples_df.values
    param_names = samples_df.columns.tolist()

    n_samples, n_params = samples_array.shape

    lines = [
        "MCMC Sample Analysis",
        "=" * 50,
        "",
        f"Dataset: {samples}",
        f"Number of samples: {n_samples:,}",
        f"Number of parameters: {n_params}",
        f"Parameters: {', '.join(param_names)}",
        "",
    ]

    pcts = np.percentile(samples_array, percentiles, axis=0)

    for i, name in enumerate(param_names):
        param_samples = samples_array[:, i]

        lines.append(f"Parameter: {name}")
        lines.append("-" * 40)
        lines.append(f"  Mean:     {np.mean(param_samples):.8f}")
        lines.append(f"  Median:   {np.median(param_samples):.8f}")
        lines.append(f"  Std Dev:  {np.std(param_samples):.8f}")
        lines.append(f"  Min:      {np.min(param_samples):.8f}")
        lines.append(f"  Max:      {np.max(param_samples):.8f}")
        lines.append("")
        lines.append("  Percentiles:")
        for j, p in enumerate(percentiles):
            lines.append(f"    {p:3d}%: {pcts[j, i]:.8f}")
        lines.append("")

    # Compute correlation matrix
    if n_params > 1:
        lines.append("Correlation Matrix:")
        lines.append("-" * 40)
        corr = np.corrcoef(samples_array.T)

        # Header
        header = "         " + " ".join(f"{name[:8]:>10s}" for name in param_names)
        lines.append(header)

        for i, name in enumerate(param_names):
            row = f"{name[:8]:<8s} " + " ".join(f"{corr[i,j]:>10.4f}" for j in range(n_params))
            lines.append(row)

    return "\n".join(lines)


@tool
def compute_best_fit_power_spectrum(
    samples: str,
    k_values: str,
    P_k_max_h_Mpc: float,
    # Fixed cosmological parameters (should match values used in MCMC)
    h: float = 0.6736,
    Omega_b: float = 0.0493,
    Omega_cdm: float = 0.264,
    A_s: float = 2.1e-9,
    n_s: float = 0.9649,
    z_pk: float = 0.0,
    use_median: bool = True
) -> str:
    """
    Compute power spectrum using best-fit parameters from MCMC samples.

    Uses either median or mean values from the posterior distribution
    to compute a theoretical power spectrum.

    Args:
        samples: dataset_name for MCMC samples DataFrame stored in session
        k_values: dataset_name for k values array stored in session (h/Mpc)
        P_k_max_h_Mpc: Maximum k for CLASS computation (h/Mpc). Must be greater than
            max(k_values) for CLASS to compute P(k) at all requested k points.
        h: Hubble parameter h = H0/100 km/s/Mpc (default: 0.6736)
        Omega_b: Baryon density parameter (default: 0.0493)
        Omega_cdm: Cold dark matter density parameter (default: 0.264)
        A_s: Scalar amplitude of primordial perturbations (default: 2.1e-9)
        n_s: Scalar spectral index (default: 0.9649)
        z_pk: Redshift for power spectrum computation (default: 0.0)
        use_median: If True, use median; if False, use mean (default: True)

    Returns:
        JSON with dataset_name referencing numpy array of P(k) values in (Mpc/h)^3.
        Use dataset_name in subsequent tool calls.

    Note:
        Fixed parameters should match those used in run_mcmc_cosmology.
        Varied parameters (from MCMC samples) will override the fixed values.
    """
    from codes.analysis import compute_power_spectrum
    import numpy as np

    session = get_session()

    # Load samples DataFrame from session
    try:
        samples_df = session.get_dataset(samples)
        samples_array = samples_df.values
        param_names = samples_df.columns.tolist()
    except KeyError as e:
        return f"Error: {str(e)}"

    # Get k_values from session first (needed for validation)
    try:
        k_data = session.get_dataset(k_values)
    except KeyError as e:
        return f"Error: {str(e)}"

    # Validate P_k_max_h_Mpc > max(k_values)
    k_max = float(np.max(k_data))
    if P_k_max_h_Mpc <= k_max:
        return json.dumps({
            "status": "error",
            "error": f"P_k_max_h_Mpc ({P_k_max_h_Mpc}) must be greater than max(k_values) ({k_max}). "
                     f"CLASS cannot compute P(k) for k values beyond P_k_max_h_Mpc."
        }, indent=2)

    # Build base_params dict from explicit primitives
    base_params = {
        'output': 'mPk',
        'P_k_max_h/Mpc': P_k_max_h_Mpc,
        'z_pk': z_pk,
        'h': h,
        'Omega_b': Omega_b,
        'Omega_cdm': Omega_cdm,
        'A_s': A_s,
        'n_s': n_s,
    }

    # Get best-fit values from posterior
    if use_median:
        best_fit = np.median(samples_array, axis=0)
    else:
        best_fit = np.mean(samples_array, axis=0)

    # Build CLASS parameters using the same mapping as MCMC sampling
    from codes.mcmc import map_params_to_class
    param_dict = {name: value for name, value in zip(param_names, best_fit)}
    class_params = map_params_to_class(param_dict, base_params)

    # Compute power spectrum
    try:
        Pk = compute_power_spectrum(class_params, k_data)
        dataset_name, info = session.store_derived(Pk, k_values, "best_fit_power_spectrum")
        return json.dumps({
            "status": "success",
            "dataset": {
                "name": dataset_name,
                "type": "array",
                "rows": info.row_count,
                "columns": ["P(k) (Mpc/h)^3"]
            },
            "parameters_used": {
                "varied": param_names,
                "best_fit_values": {name: float(val) for name, val in zip(param_names, best_fit)},
                "method": "median" if use_median else "mean"
            },
            "notes": f"Dataset '{dataset_name}' stored in session."
        }, indent=2)
    except Exception as e:
        return f"Error computing power spectrum: {str(e)}"
