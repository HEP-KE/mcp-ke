"""
MCP tool wrappers for MCMC Bayesian inference.

Provides tools for running MCMC parameter estimation, creating diagnostic plots,
and analyzing posterior distributions for cosmological models.
"""

from smolagents import tool
from typing import List, Dict, Optional
import json
from mcp_utils.session import get_session


@tool
def run_mcmc_cosmology(
    param_bounds: object,
    k_obs: str,
    Pk_obs: str,
    Pk_obs_err: str,
    base_params: dict = None,
    nwalkers: int = 32,
    nburn: int = 100,
    nrun: int = 500,
    prior_type: str = 'uniform',
    save_samples: bool = True,
    output_filename: str = None
) -> str:
    """
    Run MCMC parameter estimation for cosmological power spectrum fitting.

    This tool uses emcee (affine-invariant MCMC) to find the posterior distribution
    of cosmological parameters that best match observed power spectrum data. Works
    with any number of parameters with user-specified bounds.

    Args:
        param_bounds: List of parameter bound dictionaries, each with keys:
            - 'name' (str): Parameter name — must be a CLASS input parameter
              (e.g. 'h', 'Omega_cdm', 'Omega_b', 'A_s', 'n_s') OR a supported
              derived alias (see below).
            - 'min' (float): Minimum allowed value
            - 'max' (float): Maximum allowed value
            - 'prior_center' (float, optional): Center of Gaussian prior (only
              used when prior_type='gaussian'). Defaults to midpoint of range.
            - 'prior_sigma' (float, optional): Width of Gaussian prior (only
              used when prior_type='gaussian'). Defaults to range/4.
            Example: [{'name': 'h', 'min': 0.6, 'max': 0.8},
                      {'name': 'Omega_cdm', 'min': 0.10, 'max': 0.14}]

            Supported derived aliases (automatically mapped to CLASS inputs):
            - 'Omega_m': Total matter density. Mapped via Omega_cdm = Omega_m - Omega_b.
            - 'sum_mnu' or 'sum_nu_masses': Total neutrino mass in eV. Sets m_ncdm,
              T_ncdm, N_ur, N_ncdm.
            - 'N_ncdm_val' / 'N_eff' / 'N_species': Effective number of relativistic
              species. Sets N_ur = value - N_ncdm.
            - 'sigma8': Amplitude of matter fluctuations. Removes A_s so CLASS
              uses its shooting method.

            Example with derived params:
                [{'name': 'sigma8', 'min': 0.7, 'max': 0.9},
                 {'name': 'Omega_m', 'min': 0.2, 'max': 0.4}]

        k_obs: dataset_name from load_observational_data(), referencing numpy array
            of observed k values in h/Mpc
        Pk_obs: dataset_name from load_observational_data(), referencing numpy array
            of observed P(k) values in (Mpc/h)^3
        Pk_obs_err: dataset_name from load_observational_data(), referencing numpy array
            of P(k) uncertainties in (Mpc/h)^3
        base_params: Base CLASS parameters dict. If None, uses Planck 2018 LCDM values.
            Parameters in param_bounds will override these during sampling.
        nwalkers: Number of MCMC walkers (default: 32, recommended: 2-4x number of params)
        nburn: Number of burn-in steps to discard (default: 100)
        nrun: Number of production run steps (default: 500)
        prior_type: Prior distribution type - 'uniform' or 'gaussian' (default: 'uniform').
            When 'gaussian', supports optional 'prior_center' and 'prior_sigma' keys
            in each param_bounds dict.
        save_samples: Whether to save samples to CSV file (default: True)
        output_filename: Output CSV filename for samples (default: auto-generated)

    Returns:
        str: Summary of MCMC results including best-fit parameters, uncertainties,
             acceptance fraction, and path to saved samples file
    """
    from mcp_utils import get_output_path
    from codes.mcmc import (
        run_mcmc, extract_mcmc_results, format_mcmc_summary, save_mcmc_samples
    )
    from codes.cosmology_models import base_params as get_base_params
    import numpy as np
    from datetime import datetime
    import random

    # Parse param_bounds if it's a string
    if isinstance(param_bounds, str):
        param_bounds = json.loads(param_bounds.replace("'", '"'))

    # Get observational data from session
    session = get_session()
    k_obs = session.get_dataset(k_obs)
    Pk_obs = session.get_dataset(Pk_obs)
    Pk_obs_err = session.get_dataset(Pk_obs_err)

    # Get base parameters
    if base_params is None:
        base_params = get_base_params()

    # Validate param_bounds
    if not param_bounds or len(param_bounds) == 0:
        return "Error: param_bounds must be a non-empty list of parameter dictionaries"

    for pb in param_bounds:
        if not all(k in pb for k in ['name', 'min', 'max']):
            return f"Error: Each param_bound must have 'name', 'min', 'max' keys. Got: {pb}"
        if pb['min'] >= pb['max']:
            return f"Error: Parameter '{pb['name']}' has min >= max: {pb['min']} >= {pb['max']}"

    # Validate parameter names against known CLASS params and derived aliases
    from codes.mcmc import KNOWN_CLASS_PARAMS, DERIVED_PARAM_NAMES
    all_valid = KNOWN_CLASS_PARAMS | DERIVED_PARAM_NAMES
    for pb in param_bounds:
        if pb['name'] not in all_valid:
            return (
                f"Error: Unknown parameter '{pb['name']}'. "
                f"Must be a CLASS input parameter or a supported derived alias.\n"
                f"Supported derived aliases: Omega_m, sum_mnu/sum_nu_masses, "
                f"N_ncdm_val/N_eff/N_species, sigma8\n"
                f"Known CLASS parameters (subset): h, Omega_b, Omega_cdm, A_s, n_s, "
                f"N_ur, N_ncdm, m_ncdm, w0_fld, wa_fld, sigma8, ..."
            )

    param_names = [pb['name'] for pb in param_bounds]
    ndim = len(param_bounds)

    # Run MCMC
    try:
        mcmc_result = run_mcmc(
            param_bounds=param_bounds,
            base_params=base_params,
            k_obs=k_obs,
            Pk_obs=Pk_obs,
            Pk_obs_err=Pk_obs_err,
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

    # Format summary
    summary = format_mcmc_summary(
        results, param_names,
        mcmc_result['acceptance_fraction'],
        nwalkers, nburn, nrun
    )

    # Save samples if requested
    samples_path = None
    if save_samples:
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            process_id = random.randint(10000, 99999)
            output_filename = f"mcmc_samples_{timestamp}_pid{process_id}.csv"

        if not output_filename.endswith('.csv'):
            output_filename = output_filename + '.csv'

        samples_path = get_output_path(output_filename)
        save_mcmc_samples(samples, param_names, samples_path)
        summary += f"\n\nSamples saved to: {samples_path}"

    # Add next steps
    summary += """

Next Steps:
- Use 'create_mcmc_corner_plot' to visualize parameter posteriors
- Use 'create_mcmc_trace_plot' to check chain convergence
- Use best-fit parameters with 'compute_power_spectrum' for predictions
"""

    return summary


@tool
def create_mcmc_corner_plot(
    samples_csv: str,
    param_labels: dict = None,
    param_ranges: dict = None,
    title: str = None,
    smooth_scale: float = 1.0,
    output_filename: str = None
) -> str:
    """
    Create corner plot (triangle plot) from MCMC samples showing parameter posteriors.

    Generates publication-quality corner plots visualizing posterior distributions
    and correlations between parameters using GetDist for kernel density estimation.

    Args:
        samples_csv: Path to CSV file with MCMC samples (output from run_mcmc_cosmology)
        param_labels: Optional dict mapping parameter names to LaTeX labels for display.
            IMPORTANT: Do NOT include $ delimiters - GetDist adds them automatically.
            Example: {'h': r'H_0/100', 'Omega_cdm': r'\\Omega_{\\rm cdm}'}
        param_ranges: Optional dict mapping parameter names to (min, max) plot ranges.
            Example: {'h': (0.65, 0.70), 'Omega_cdm': (0.11, 0.13)}
        title: Optional title for the plot
        smooth_scale: Smoothing scale for KDE (default: 1.0, larger = smoother)
        output_filename: Output filename for the plot (default: auto-generated)

    Returns:
        str: Summary with plot file path and parameter statistics
    """
    from mcp_utils import get_output_path
    from codes.mcmc import load_mcmc_samples, create_corner_plot, extract_mcmc_results
    import os
    from datetime import datetime
    import random

    # Check file exists
    if not os.path.exists(samples_csv):
        return f"Error: Samples file not found: {samples_csv}"

    # Load samples
    try:
        samples, param_names = load_mcmc_samples(samples_csv)
    except Exception as e:
        return f"Error loading samples: {str(e)}"

    n_samples, n_params = samples.shape

    # Determine output path
    if output_filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        process_id = random.randint(10000, 99999)
        output_filename = f"mcmc_corner_{timestamp}_pid{process_id}.png"

    if not output_filename.endswith('.png'):
        output_filename = output_filename + '.png'

    output_path = get_output_path(output_filename)

    # Create corner plot
    try:
        plot_path = create_corner_plot(
            samples, param_names,
            param_labels=param_labels,
            param_ranges=param_ranges,
            title=title,
            smooth_scale=smooth_scale,
            output_path=output_path
        )
    except Exception as e:
        return f"Error creating corner plot: {str(e)}"

    # Compute statistics
    results = extract_mcmc_results(samples, param_names)

    summary_lines = [
        "MCMC Corner Plot Created",
        "=" * 40,
        "",
        f"Samples file: {samples_csv}",
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
    samples_csv: str,
    param_labels: dict = None,
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
        samples_csv: Path to CSV file with MCMC samples
        param_labels: Optional dict mapping parameter names to display labels
            Include $ delimiters for LaTeX: {'h': r'$H_0/100$'}
        max_samples: Maximum number of samples to plot for performance (default: 5000)
        output_filename: Output filename for the plot (default: auto-generated)

    Returns:
        str: Summary with plot file path and convergence guidance
    """
    from mcp_utils import get_output_path
    from codes.mcmc import load_mcmc_samples, create_trace_plot
    import os
    from datetime import datetime
    import random

    # Check file exists
    if not os.path.exists(samples_csv):
        return f"Error: Samples file not found: {samples_csv}"

    # Load samples
    try:
        samples, param_names = load_mcmc_samples(samples_csv)
    except Exception as e:
        return f"Error loading samples: {str(e)}"

    n_samples, n_params = samples.shape

    # Determine output path
    if output_filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        process_id = random.randint(10000, 99999)
        output_filename = f"mcmc_trace_{timestamp}_pid{process_id}.png"

    if not output_filename.endswith('.png'):
        output_filename = output_filename + '.png'

    output_path = get_output_path(output_filename)

    # Create trace plot
    try:
        plot_path = create_trace_plot(
            samples, param_names,
            param_labels=param_labels,
            output_path=output_path,
            max_samples=max_samples
        )
    except Exception as e:
        return f"Error creating trace plot: {str(e)}"

    samples_plotted = min(n_samples, max_samples)

    summary = f"""MCMC Trace Plot Created
========================================

Samples file: {samples_csv}
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
    samples_csv: str,
    percentiles: object = None
) -> str:
    """
    Analyze MCMC samples and compute parameter statistics.

    Computes summary statistics including mean, median, standard deviation,
    and credible intervals for all sampled parameters.

    Args:
        samples_csv: Path to CSV file with MCMC samples
        percentiles: List of percentiles to compute (default: [5, 16, 50, 84, 95])

    Returns:
        str: Detailed statistics for each parameter
    """
    from codes.mcmc import load_mcmc_samples
    import numpy as np
    import os

    if percentiles is None:
        percentiles = [5, 16, 50, 84, 95]

    # Check file exists
    if not os.path.exists(samples_csv):
        return f"Error: Samples file not found: {samples_csv}"

    # Load samples
    try:
        samples, param_names = load_mcmc_samples(samples_csv)
    except Exception as e:
        return f"Error loading samples: {str(e)}"

    n_samples, n_params = samples.shape

    lines = [
        "MCMC Sample Analysis",
        "=" * 50,
        "",
        f"Samples file: {samples_csv}",
        f"Number of samples: {n_samples:,}",
        f"Number of parameters: {n_params}",
        "",
    ]

    pcts = np.percentile(samples, percentiles, axis=0)

    for i, name in enumerate(param_names):
        param_samples = samples[:, i]

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
        corr = np.corrcoef(samples.T)

        # Header
        header = "         " + " ".join(f"{name[:8]:>10s}" for name in param_names)
        lines.append(header)

        for i, name in enumerate(param_names):
            row = f"{name[:8]:<8s} " + " ".join(f"{corr[i,j]:>10.4f}" for j in range(n_params))
            lines.append(row)

    return "\n".join(lines)


@tool
def compute_best_fit_power_spectrum(
    samples_csv: str,
    k_values: str,
    base_params: dict = None,
    use_median: bool = True
) -> str:
    """
    Compute power spectrum using best-fit parameters from MCMC samples.

    Uses either median or mean values from the posterior distribution
    to compute a theoretical power spectrum.

    Args:
        samples_csv: Path to CSV file with MCMC samples
        k_values: dataset_name from create_theory_k_grid(), referencing numpy array
            of k values in h/Mpc for P(k) computation
        base_params: Base CLASS parameters dict. If None, uses Planck 2018 LCDM values.
        use_median: If True, use median; if False, use mean (default: True)

    Returns:
        JSON with dataset_name referencing numpy array of P(k) values in (Mpc/h)^3.
        Use dataset_name in subsequent tool calls.
    """
    from codes.mcmc import load_mcmc_samples
    from codes.analysis import compute_power_spectrum
    from codes.cosmology_models import base_params as get_base_params
    import numpy as np
    import os

    # Check file exists
    if not os.path.exists(samples_csv):
        return f"Error: Samples file not found: {samples_csv}"

    # Load samples
    try:
        samples, param_names = load_mcmc_samples(samples_csv)
    except Exception as e:
        return f"Error loading samples: {str(e)}"

    # Get best-fit values
    if use_median:
        best_fit = np.median(samples, axis=0)
    else:
        best_fit = np.mean(samples, axis=0)

    # Get base parameters
    if base_params is None:
        base_params = get_base_params()

    # Build CLASS parameters using the same mapping as MCMC sampling
    from codes.mcmc import map_params_to_class
    param_dict = {name: value for name, value in zip(param_names, best_fit)}
    class_params = map_params_to_class(param_dict, base_params)

    # Get k_values from session
    session = get_session()
    k_data = session.get_dataset(k_values)

    # Compute power spectrum
    try:
        Pk = compute_power_spectrum(class_params, k_data)
        dataset_name, info = session.store_derived(Pk, k_values, "best_fit_power_spectrum")
        return json.dumps({"dataset_name": dataset_name, "row_count": info.row_count}, indent=2)
    except Exception as e:
        return f"Error computing power spectrum: {str(e)}"
