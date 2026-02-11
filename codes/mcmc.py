"""
MCMC Bayesian inference for cosmological parameter estimation using CLASS.

This module provides generic MCMC functionality that works with arbitrary
cosmological models and parameter sets defined in cosmology_models.py.
"""

import numpy as np
import os
from datetime import datetime
import random

from .analysis import compute_power_spectrum


# Known CLASS input parameters (covers all models in cosmology_models.py)
KNOWN_CLASS_PARAMS = {
    'h', 'H0', 'omega_b', 'Omega_b', 'omega_cdm', 'Omega_cdm',
    'A_s', 'ln10^{10}A_s', 'sigma8', 'n_s', 'alpha_s', 'tau_reio',
    'N_ur', 'N_ncdm', 'm_ncdm', 'T_ncdm', 'Omega_ncdm',
    'Omega_k', 'Omega_Lambda', 'Omega_fld', 'w0_fld', 'wa_fld',
    'f_idm', 'N_idr', 'a_idm_dr', 'nindex_idm_dr', 'idr_nature',
    'alpha_idm_dr', 'output', 'P_k_max_h/Mpc', 'z_pk',
    '_w0_approx',   # internal key used by wCDM model
}

# Derived parameters that can be mapped to CLASS parameters
DERIVED_PARAM_NAMES = {'Omega_m', 'sum_mnu', 'N_ncdm_val', 'N_eff'}


def map_params_to_class(param_dict, base_params):
    """
    Map sampled parameter names to valid CLASS input parameters.

    Handles direct CLASS parameters (pass-through) and derived aliases
    (Omega_m, sum_mnu, N_ncdm_val/N_eff, sigma8) by converting them
    to the corresponding CLASS inputs.

    Args:
        param_dict: Dict of {param_name: value} from the sampler
        base_params: Base CLASS parameters dict (used to look up h, N_ncdm, etc.)

    Returns:
        dict: Updated copy of base_params with mapped parameters applied

    Raises:
        ValueError: If a parameter name is neither a known CLASS param nor
                    a supported derived alias
    """
    class_params = base_params.copy()

    for name, value in param_dict.items():
        if name in KNOWN_CLASS_PARAMS:
            # Direct CLASS parameter — pass through
            class_params[name] = value
            # sigma8: remove A_s so CLASS uses its shooting method
            if name == 'sigma8':
                class_params.pop('A_s', None)
                class_params.pop('ln10^{10}A_s', None)

        elif name == 'Omega_m':
            # Derive Omega_cdm from Omega_m: Omega_cdm = Omega_m - Omega_b
            h = class_params.get('h', base_params.get('h', 0.67556))
            Omega_b = class_params.get('Omega_b', base_params.get('Omega_b', 0.022032))
            class_params['Omega_cdm'] = value - Omega_b

        elif name == 'sum_mnu':
            # Total neutrino mass in eV → set m_ncdm, T_ncdm, N_ur, N_ncdm
            N_ncdm = int(class_params.get('N_ncdm', base_params.get('N_ncdm', 1)))
            m_per_species = value / N_ncdm
            class_params['N_ncdm'] = N_ncdm
            class_params['m_ncdm'] = ','.join([str(m_per_species)] * N_ncdm)
            T_val = '0.71611'
            class_params['T_ncdm'] = ','.join([T_val] * N_ncdm) if N_ncdm > 1 else float(T_val)
            class_params['N_ur'] = 3.044 - N_ncdm

        elif name in ('N_ncdm_val', 'N_eff'):
            # Continuous effective number of relativistic species
            N_ncdm = int(class_params.get('N_ncdm', base_params.get('N_ncdm', 0)))
            class_params['N_ur'] = value - N_ncdm

        else:
            valid = sorted(KNOWN_CLASS_PARAMS | DERIVED_PARAM_NAMES)
            raise ValueError(
                f"Unknown parameter '{name}'. Must be a CLASS input parameter "
                f"or a supported derived alias.\n"
                f"Supported derived aliases: Omega_m, sum_mnu, N_ncdm_val, N_eff, sigma8\n"
                f"Known CLASS parameters: {valid}"
            )

    return class_params


def ln_prior_uniform(theta, param_bounds):
    """
    Compute log prior probability with uniform priors within bounds.

    Args:
        theta: Array of parameter values
        param_bounds: List of dicts with keys 'name', 'min', 'max' for each parameter

    Returns:
        float: Log prior probability (0 if within bounds, -inf otherwise)
    """
    for val, bounds in zip(theta, param_bounds):
        if not (bounds['min'] < val < bounds['max']):
            return -np.inf
    return 0.0


def ln_prior_gaussian(theta, param_bounds):
    """
    Compute log prior probability with Gaussian priors centered in parameter ranges.

    Args:
        theta: Array of parameter values
        param_bounds: List of dicts with keys 'name', 'min', 'max' for each parameter

    Returns:
        float: Log prior probability
    """
    log_prob = 0.0
    for val, bounds in zip(theta, param_bounds):
        min_val, max_val = bounds['min'], bounds['max']

        # Uniform bounds check first
        if not (min_val < val < max_val):
            return -np.inf

        # Gaussian prior: honor user-supplied center/sigma, else default
        mu = bounds.get('prior_center', 0.5 * (max_val + min_val))
        sigma = bounds.get('prior_sigma', (max_val - min_val) / 4.0)
        log_prob += -0.5 * ((val - mu) / sigma) ** 2

    return log_prob


def log_likelihood_power_spectrum(theta, param_bounds, base_params, k_obs, Pk_obs,
                                   Pk_obs_err, model_func=None):
    """
    Compute log likelihood comparing theoretical P(k) to observations.

    Args:
        theta: Array of parameter values being sampled
        param_bounds: List of dicts with 'name', 'min', 'max' for each parameter
        base_params: Base CLASS parameters dict to modify
        k_obs: Array of observed k values (h/Mpc)
        Pk_obs: Array of observed P(k) values
        Pk_obs_err: Array of P(k) uncertainties
        model_func: Optional function(base_params, param_dict) -> CLASS params
                   If None, directly updates base_params with param values

    Returns:
        float: Log likelihood
    """
    # Build parameter dictionary from theta
    param_dict = {}
    for val, bounds in zip(theta, param_bounds):
        param_dict[bounds['name']] = val

    # Create CLASS parameters
    if model_func is not None:
        class_params = model_func(base_params.copy(), param_dict)
    else:
        class_params = map_params_to_class(param_dict, base_params)

    # Compute theoretical P(k)
    try:
        Pk_theory = compute_power_spectrum(class_params, k_obs)
        if isinstance(Pk_theory, str) and Pk_theory.startswith("Error"):
            return -np.inf
    except Exception:
        return -np.inf

    # Gaussian likelihood
    chi2 = np.sum(((Pk_obs - Pk_theory) / Pk_obs_err) ** 2)
    return -0.5 * chi2


def ln_posterior(theta, param_bounds, base_params, k_obs, Pk_obs, Pk_obs_err,
                 prior_type='uniform', model_func=None):
    """
    Compute log posterior probability (prior + likelihood).

    Args:
        theta: Array of parameter values
        param_bounds: List of dicts with 'name', 'min', 'max' for each parameter
        base_params: Base CLASS parameters
        k_obs: Observed k values
        Pk_obs: Observed P(k) values
        Pk_obs_err: P(k) uncertainties
        prior_type: 'uniform' or 'gaussian'
        model_func: Optional function to transform parameters to CLASS params

    Returns:
        float: Log posterior probability
    """
    # Evaluate prior
    if prior_type == 'gaussian':
        lp = ln_prior_gaussian(theta, param_bounds)
    else:
        lp = ln_prior_uniform(theta, param_bounds)

    if not np.isfinite(lp):
        return -np.inf

    # Evaluate likelihood
    ll = log_likelihood_power_spectrum(
        theta, param_bounds, base_params, k_obs, Pk_obs, Pk_obs_err, model_func
    )

    return lp + ll


def initialize_walkers(param_bounds, nwalkers, init_method='uniform'):
    """
    Initialize MCMC walker positions.

    Args:
        param_bounds: List of dicts with 'name', 'min', 'max' for each parameter
        nwalkers: Number of walkers
        init_method: 'uniform' (random in bounds) or 'center' (near center of bounds)

    Returns:
        np.ndarray: Initial positions (nwalkers, ndim)
    """
    ndim = len(param_bounds)
    pos0 = np.zeros((nwalkers, ndim))

    for i, bounds in enumerate(param_bounds):
        min_val, max_val = bounds['min'], bounds['max']
        center = 0.5 * (min_val + max_val)
        width = max_val - min_val

        if init_method == 'center':
            # Initialize near center with small scatter
            pos0[:, i] = center + 0.1 * width * np.random.randn(nwalkers)
            # Clip to bounds
            pos0[:, i] = np.clip(pos0[:, i], min_val + 0.01*width, max_val - 0.01*width)
        else:
            # Uniform random initialization
            pos0[:, i] = np.random.uniform(min_val, max_val, nwalkers)

    return pos0


def run_mcmc(param_bounds, base_params, k_obs, Pk_obs, Pk_obs_err,
             nwalkers=32, nburn=100, nrun=500, prior_type='uniform',
             model_func=None, init_method='uniform', progress=False):
    """
    Run MCMC parameter estimation for cosmological power spectrum.

    Args:
        param_bounds: List of dicts with 'name', 'min', 'max' for each parameter
            Example: [{'name': 'h', 'min': 0.6, 'max': 0.8},
                      {'name': 'Omega_cdm', 'min': 0.1, 'max': 0.15}]
        base_params: Base CLASS parameters dict
        k_obs: Array of observed k values (h/Mpc)
        Pk_obs: Array of observed P(k) values
        Pk_obs_err: Array of P(k) uncertainties
        nwalkers: Number of MCMC walkers (default: 32)
        nburn: Number of burn-in steps (default: 100)
        nrun: Number of production steps (default: 500)
        prior_type: 'uniform' or 'gaussian' (default: 'uniform')
        model_func: Optional function(base_params, param_dict) -> CLASS params
        init_method: Walker initialization method (default: 'uniform')
        progress: Show progress bar if True (default: False)

    Returns:
        dict: Results containing:
            - 'samples': Flattened chain samples (n_samples, ndim)
            - 'param_names': List of parameter names
            - 'param_bounds': The input param_bounds
            - 'chain': Full chain (nwalkers, nsteps, ndim)
            - 'log_prob': Log probability values
            - 'acceptance_fraction': Mean acceptance fraction
            - 'nwalkers': Number of walkers
            - 'nburn': Burn-in steps
            - 'nrun': Production steps
    """
    try:
        import emcee
    except ImportError:
        raise ImportError("emcee package required. Install with: pip install emcee")

    ndim = len(param_bounds)
    param_names = [b['name'] for b in param_bounds]

    # Initialize walkers
    pos0 = initialize_walkers(param_bounds, nwalkers, init_method)

    # Create sampler
    sampler = emcee.EnsembleSampler(
        nwalkers, ndim, ln_posterior,
        args=(param_bounds, base_params, k_obs, Pk_obs, Pk_obs_err, prior_type, model_func)
    )

    # Burn-in
    pos, prob, state = sampler.run_mcmc(pos0, nburn, progress=progress)
    sampler.reset()

    # Production run
    sampler.run_mcmc(pos, nrun, progress=progress)

    # Extract results
    samples = sampler.get_chain(flat=True)
    chain = sampler.get_chain()
    log_prob = sampler.get_log_prob(flat=True)
    acceptance = np.mean(sampler.acceptance_fraction)

    return {
        'samples': samples,
        'param_names': param_names,
        'param_bounds': param_bounds,
        'chain': chain,
        'log_prob': log_prob,
        'acceptance_fraction': acceptance,
        'nwalkers': nwalkers,
        'nburn': nburn,
        'nrun': nrun,
    }


def extract_mcmc_results(samples, param_names, percentiles=(16, 50, 84)):
    """
    Extract parameter constraints from MCMC samples.

    Args:
        samples: MCMC samples array (n_samples, ndim)
        param_names: List of parameter names
        percentiles: Tuple of percentiles for credible intervals (default: 16, 50, 84)

    Returns:
        dict: Dictionary with parameter names as keys, values are dicts containing:
            - 'median': Median value
            - 'mean': Mean value
            - 'std': Standard deviation
            - 'lower': Lower percentile
            - 'upper': Upper percentile
            - 'upper_err': Upper error (upper - median)
            - 'lower_err': Lower error (median - lower)
    """
    results = {}
    pcts = np.percentile(samples, percentiles, axis=0)

    for i, name in enumerate(param_names):
        lower, median, upper = pcts[0, i], pcts[1, i], pcts[2, i]
        results[name] = {
            'median': median,
            'mean': np.mean(samples[:, i]),
            'std': np.std(samples[:, i]),
            'lower': lower,
            'upper': upper,
            'upper_err': upper - median,
            'lower_err': median - lower,
        }

    return results


def save_mcmc_samples(samples, param_names, output_path):
    """
    Save MCMC samples to CSV file.

    Args:
        samples: MCMC samples array (n_samples, ndim)
        param_names: List of parameter names
        output_path: Path to save CSV file

    Returns:
        str: Path to saved file
    """
    import csv

    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(param_names)
        for row in samples:
            writer.writerow(row)

    return output_path


def load_mcmc_samples(csv_path):
    """
    Load MCMC samples from CSV file.

    Args:
        csv_path: Path to CSV file

    Returns:
        tuple: (samples array, param_names list)
    """
    import csv

    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        param_names = next(reader)
        samples = np.array([[float(x) for x in row] for row in reader])

    return samples, param_names


def create_corner_plot(samples, param_names, param_labels=None, param_ranges=None,
                       title=None, smooth_scale=1.0, output_path=None):
    """
    Create corner plot from MCMC samples showing parameter posteriors.

    Args:
        samples: MCMC samples array (n_samples, ndim)
        param_names: List of parameter names
        param_labels: Optional dict mapping param names to LaTeX labels
                     (do NOT include $ delimiters)
        param_ranges: Optional dict mapping param names to (min, max) tuples
        title: Optional plot title
        smooth_scale: Smoothing scale for KDE (default: 1.0)
        output_path: Path to save plot. If None, generates default path.

    Returns:
        str: Path to saved plot
    """
    try:
        from getdist import MCSamples, plots
    except ImportError:
        raise ImportError("getdist package required. Install with: pip install getdist")

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    from mcp_utils import get_output_path

    n_samples, n_params = samples.shape

    # Setup labels
    if param_labels is not None:
        labels = [param_labels.get(p, p) for p in param_names]
    else:
        labels = param_names

    # Setup ranges
    ranges_dict = {}
    if param_ranges is not None:
        for p in param_names:
            if p in param_ranges:
                idx = param_names.index(p)
                ranges_dict[labels[idx]] = param_ranges[p]

    # Create MCSamples object
    # Redirect stdout to stderr during GetDist calls: GetDist prints messages
    # like "Removed no burn in" to stdout, which corrupts MCP's JSON-RPC
    # stdio protocol.
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        mc_samples = MCSamples(
            samples=samples,
            names=param_names,
            labels=labels,
            settings={
                'mult_bias_correction_order': 0.5,
                'smooth_scale_2D': 2.0 * smooth_scale,
                'smooth_scale_1D': 2.0 * smooth_scale
            }
        )

    # Create corner plot
    g = plots.get_subplot_plotter(subplot_size=2.5)
    g.settings.axes_fontsize = 12
    g.settings.axes_labelsize = 14
    g.settings.legend_fontsize = 12
    g.settings.fontsize = 12
    g.settings.alpha_filled_add = 0.8
    g.settings.solid_contour_palefactor = 0.6
    g.settings.num_plot_contours = 2

    with contextlib.redirect_stdout(io.StringIO()):
        g.triangle_plot(
            mc_samples,
            param_names,
            filled=True,
            param_limits=ranges_dict if ranges_dict else {}
        )

    if title:
        g.fig.suptitle(title, fontsize=10, y=0.999)

    # Determine output path
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        process_id = random.randint(10000, 99999)
        filename = f"mcmc_corner_{timestamp}_pid{process_id}.png"
        output_path = get_output_path(filename)

    g.fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(g.fig)

    return output_path


def create_trace_plot(chain, param_names, param_labels=None, output_path=None,
                      max_samples=5000):
    """
    Create trace plots showing MCMC chain evolution.

    Args:
        chain: MCMC chain array (nwalkers, nsteps, ndim) or flattened (n_samples, ndim)
        param_names: List of parameter names
        param_labels: Optional dict mapping param names to display labels
        output_path: Path to save plot. If None, generates default path.
        max_samples: Maximum samples to plot for performance (default: 5000)

    Returns:
        str: Path to saved plot
    """
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    from mcp_utils import get_output_path

    # Handle both chain shapes
    if chain.ndim == 3:
        # (nwalkers, nsteps, ndim) -> flatten to (n_samples, ndim)
        nwalkers, nsteps, ndim = chain.shape
        samples = chain.reshape(-1, ndim)
    else:
        samples = chain

    n_samples, n_params = samples.shape

    # Downsample if needed
    if n_samples > max_samples:
        step = n_samples // max_samples
        samples = samples[::step]
        n_samples = len(samples)

    # Setup labels
    if param_labels is not None:
        labels = [f"${param_labels.get(p, p)}$" for p in param_names]
    else:
        labels = param_names

    # Create plot
    fig, axes = plt.subplots(n_params, 1, figsize=(10, 2 * n_params), sharex=True)
    if n_params == 1:
        axes = [axes]

    for i, (name, label) in enumerate(zip(param_names, labels)):
        ax = axes[i]
        values = samples[:, i]

        ax.plot(values, alpha=0.7, linewidth=0.5, color='steelblue')
        ax.set_ylabel(label, fontsize=11)
        ax.grid(True, alpha=0.3)

        # Add median line
        median = np.median(values)
        ax.axhline(median, color='red', linestyle='--', linewidth=1, alpha=0.7)

    axes[-1].set_xlabel('Sample Number', fontsize=11)
    fig.suptitle('MCMC Trace Plots', fontsize=14, y=0.995)
    fig.tight_layout()

    # Determine output path
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        process_id = random.randint(10000, 99999)
        filename = f"mcmc_trace_{timestamp}_pid{process_id}.png"
        output_path = get_output_path(filename)

    fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)

    return output_path


def format_mcmc_summary(results, param_names, acceptance_fraction, nwalkers, nburn, nrun):
    """
    Format MCMC results as a human-readable summary string.

    Args:
        results: Dictionary from extract_mcmc_results()
        param_names: List of parameter names
        acceptance_fraction: Mean acceptance fraction
        nwalkers: Number of walkers
        nburn: Burn-in steps
        nrun: Production steps

    Returns:
        str: Formatted summary
    """
    lines = [
        "MCMC Parameter Estimation Results",
        "=" * 40,
        "",
        f"Configuration:",
        f"  Walkers: {nwalkers}",
        f"  Burn-in steps: {nburn}",
        f"  Production steps: {nrun}",
        f"  Total samples: {nwalkers * nrun:,}",
        f"  Acceptance fraction: {acceptance_fraction:.3f}",
        "",
        "Parameter Constraints (68% credible intervals):",
        "-" * 40,
    ]

    for name in param_names:
        r = results[name]
        lines.append(f"  {name}:")
        lines.append(f"    Median: {r['median']:.6f} +{r['upper_err']:.6f} -{r['lower_err']:.6f}")
        lines.append(f"    Mean:   {r['mean']:.6f} +/- {r['std']:.6f}")

    return "\n".join(lines)
