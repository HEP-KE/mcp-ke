"""
Visualization functions for cosmological power spectra
"""

import matplotlib.pyplot as plt
import numpy as np

def plot_power_spectra(k_theory, model_results, k_obs, Pk_obs, σPk_obs,
                       save_path='plots/matter_power_spectrum_comparison.png'):
    """
    Create plot comparing theoretical models with observations.

    Args:
        k_theory: k values for theoretical models
        model_results: Dictionary with model names and P(k) arrays
        k_obs: k values for observations
        Pk_obs: P(k) values for observations
        σPk_obs: Errors on P(k) observations
        save_path: Path to save the figure
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 10),
                                    gridspec_kw={'height_ratios': [2, 1], 'hspace': 0.05})

    # Define colors for different model categories
    colors = {
        'ΛCDM': 'black',
        'ΛCDM + Σmν=0.06 eV': 'cyan',
        'ΛCDM + Σmν=0.10 eV': 'blue',
        'wCDM (w0=-0.9)': 'red',
        'wCDM (w0=-1.1)': 'darkred',
        'Thermal WDM (all DM, m=3 keV)': 'green',
        'CWDM (f_wdm=0.2, m=3 keV, g*=100)': 'orange',
        'ETHOS IDM–DR (fiducial)': 'purple',
        'IDM–baryon (σ=1e-41 cm², n=-4)': 'brown',
    }

    # Define linestyles for visual distinction
    linestyles = {
        'ΛCDM': '-',
        'ΛCDM + Σmν=0.06 eV': '--',
        'ΛCDM + Σmν=0.10 eV': '--',
        'wCDM (w0=-0.9)': '-.',
        'wCDM (w0=-1.1)': '-.',
        'Thermal WDM (all DM, m=3 keV)': ':',
        'CWDM (f_wdm=0.2, m=3 keV, g*=100)': '--',
        'ETHOS IDM–DR (fiducial)': '-.',
        'IDM–baryon (σ=1e-41 cm², n=-4)': ':',
    }

    # Get ΛCDM for ratio
    P_lcdm = model_results.get('ΛCDM', None)

    # ===== TOP PANEL: Power Spectrum =====
    # Plot theoretical predictions
    for model_name, Pk_model in model_results.items():
        if Pk_model is not None:
            color = colors.get(model_name, 'gray')
            linestyle = linestyles.get(model_name, '-')
            ax1.loglog(k_theory, Pk_model,
                      color=color,
                      linestyle=linestyle,
                      linewidth=1.5,
                      label=model_name,
                      alpha=0.9)

    # Plot observational data
    if k_obs is not None and Pk_obs is not None:
        ax1.errorbar(k_obs, Pk_obs, yerr=σPk_obs,
                    fmt='ko', markersize=5,
                    label='DR14 LyA forest',
                    alpha=0.8,
                    capsize=3,
                    markerfacecolor='none',
                    markeredgewidth=1.5)

    # Formatting top panel
    ax1.set_ylabel('P(k) [(Mpc/h)³]', fontsize='x-large')
    ax1.set_title('Matter Power Spectrum: Theory vs Observations', fontsize='x-large')
    ax1.legend(loc='lower left', fontsize='medium', framealpha=0.95, ncol=1)
    ax1.set_xlim(1e-4, 20)
    ax1.set_ylim(1e0, 2e5)
    ax1.tick_params(labelbottom=False)
    # ax1.grid(True, alpha=0.3, which='both')

    # ===== BOTTOM PANEL: Ratio to ΛCDM =====
    if P_lcdm is not None:
        # Plot model ratios
        for model_name, Pk_model in model_results.items():
            if Pk_model is not None and model_name != 'ΛCDM':
                color = colors.get(model_name, 'gray')
                linestyle = linestyles.get(model_name, '-')
                ratio = Pk_model / P_lcdm
                ax2.semilogx(k_theory, ratio,
                           color=color,
                           linestyle=linestyle,
                           linewidth=1.5,
                           alpha=0.9)

        # Compute ΛCDM theory at observed k points for ratio
        if k_obs is not None and Pk_obs is not None:
            # Interpolate ΛCDM to observed k points
            P_lcdm_interp = np.interp(k_obs, k_theory, P_lcdm)
            ratio_obs = Pk_obs / P_lcdm_interp
            ratio_obs_err = σPk_obs / P_lcdm_interp

            ax2.errorbar(k_obs, ratio_obs, yerr=ratio_obs_err,
                        fmt='ko', markersize=5,
                        alpha=0.8,
                        capsize=3,
                        markerfacecolor='none',
                        markeredgewidth=1.5)

        # Reference line at 1
        ax2.axhline(y=1, color='black', linestyle='-', linewidth=1.5, alpha=0.9)

    # Formatting bottom panel
    ax2.set_xlabel('k [h/Mpc]', fontsize='x-large')
    ax2.set_ylabel('P(k) / P$_{\\Lambda CDM}$(k)', fontsize='x-large')
    ax2.set_xlim(1e-4, 20)
    ax2.set_ylim(0.0, 1.5)
    # ax2.grid(True, alpha=0.3, which='both')

    plt.tight_layout()

    # Save figure if path provided
    if save_path is not None:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    # plt.show()

    return fig


def plot_suppression_ratios(k_values, suppression_ratios, reference_model='ΛCDM',
                           save_path='plots/power_spectrum_suppression.png'):
    """
    Plot power spectrum suppression relative to reference model.
    
    Args:
        k_values: Array of k values
        suppression_ratios: Dictionary with model names and suppression arrays
        reference_model: Name of the reference model
        save_path: Path to save the figure
    """
    plt.figure(figsize=(9, 7))
    
    # Define colors for different models
    colors = {
        'ΛCDM + Σmν=0.06 eV': 'cyan',
        'ΛCDM + Σmν=0.10 eV': 'blue',
        'wCDM (w0=-0.9)': 'red',
        'wCDM (w0=-1.1)': 'darkred',
        'Thermal WDM (all DM, m=3 keV)': 'green',
        'CWDM (f_wdm=0.2, m=3 keV, g*=100)': 'orange',
        'ETHOS IDM–DR (fiducial)': 'purple',
        'IDM–baryon (σ=1e-41 cm², n=-4)': 'brown',
    }
    
    # Plot suppression ratios
    for model_name, ratio in suppression_ratios.items():
        color = colors.get(model_name, 'gray')
        plt.semilogx(k_values, ratio, 
                    color=color, 
                    linewidth=1.5, 
                    label=model_name, 
                    alpha=0.9)
    
    # Add reference line at 1
    plt.axhline(y=1, color='black', linestyle='--', alpha=0.5, label=reference_model)
    
    # Add shaded regions for different suppression levels
    plt.axhspan(0.9, 1.0, alpha=0.25, color='blue', label='10% suppression')
    plt.axhspan(0.5, 0.9, alpha=0.15, color='red', label='10-50% suppression')
    
    # Formatting
    plt.xlabel('k [h/Mpc]', fontsize='x-large')
    plt.ylabel(f'P(k) / P_{{{reference_model}}}(k)', fontsize='x-large')
    plt.title(f'Power Spectrum Suppression Relative to {reference_model}', fontsize='x-large')
    plt.legend(loc='best', fontsize='x-large', framealpha=0.95)
    plt.xlim(1e-3, 20)
    plt.ylim(0.3, 1.3)
    # plt.grid(True, alpha=0.3)
    plt.tight_layout()

    # Save figure if path provided
    if save_path is not None:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    # plt.show()

    return plt.gcf()


def plot_model_comparison_grid(k_values, model_results, reference_model='ΛCDM',
                              save_path='plots/model_comparison_grid.png'):
    """
    Create a grid of subplots comparing each model to the reference.
    
    Args:
        k_values: Array of k values
        model_results: Dictionary with model names and P(k) arrays
        reference_model: Name of the reference model
        save_path: Path to save the figure
    """
    # Filter out the reference model
    models_to_plot = {k: v for k, v in model_results.items() if k != reference_model}
    n_models = len(models_to_plot)
    
    if n_models == 0:
        return None
    
    # Create subplot grid
    n_cols = 3
    n_rows = (n_models + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4*n_rows))
    if n_rows == 1:
        axes = axes.reshape(1, -1)
    
    # Get reference power spectrum
    P_ref = model_results[reference_model]
    
    # Plot each model
    for idx, (model_name, Pk) in enumerate(models_to_plot.items()):
        row = idx // n_cols
        col = idx % n_cols
        ax = axes[row, col]
        
        # Plot ratio
        ratio = Pk / P_ref
        ax.semilogx(k_values, ratio, 'b-', linewidth=2)
        ax.axhline(y=1, color='k', linestyle='--', alpha=0.5)
        
        # Formatting
        ax.set_xlabel('k [h/Mpc]', fontsize='x-large')
        ax.set_ylabel(f'P/P_{{{reference_model}}}', fontsize='x-large')
        ax.set_title(model_name, fontsize='x-large', wrap=True)
        ax.set_xlim(1e-3, 20)
        ax.set_ylim(0, 1.2)
        # ax.grid(True, alpha=0.3)
    
    # Hide empty subplots
    for idx in range(n_models, n_rows * n_cols):
        row = idx // n_cols
        col = idx % n_cols
        axes[row, col].set_visible(False)
    
    plt.suptitle(f'Model Comparisons Relative to {reference_model}', fontsize='x-large')
    plt.tight_layout()

    # Save figure if path provided
    if save_path is not None:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    # plt.show()

    return fig


def plot_scale_dependent_effects(k_values, model_results, 
                                k_markers=[0.01, 0.1, 1.0, 10.0],
                                save_path='plots/scale_dependent_effects.png'):
    """
    Visualize scale-dependent effects of different models.
    
    Args:
        k_values: Array of k values
        model_results: Dictionary with model names and P(k) arrays
        k_markers: List of k values to mark
        save_path: Path to save the figure
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 7))
    
    # Top panel: Power spectra
    for model_name, Pk in model_results.items():
        if Pk is not None:
            ax1.loglog(k_values, Pk, label=model_name, linewidth=2, alpha=0.8)
    
    # Mark specific k values
    for k_mark in k_markers:
        ax1.axvline(x=k_mark, color='gray', linestyle=':', alpha=0.5)
        ax1.text(k_mark, ax1.get_ylim()[1]*0.8, f'k={k_mark}', 
                rotation=90, va='top', ha='right', fontsize='x-large')
    
    ax1.set_ylabel('P(k) [(Mpc/h)³]', fontsize='x-large')
    ax1.set_title('Matter Power Spectrum', fontsize='x-large')
    ax1.legend(loc='lower left', fontsize='x-large', ncol=1)
    # ax1.grid(True, alpha=0.3, which='both')
    
    # Bottom panel: Transfer functions (sqrt(P/P_primordial))
    if 'ΛCDM' in model_results:
        # Compute approximate transfer functions
        A_s = 2.215e-9
        n_s = 0.9619
        h = 0.67556
        
        for model_name, Pk in model_results.items():
            if Pk is not None:
                # Approximate primordial power spectrum
                P_prim = A_s * (k_values * h / 0.05) ** (n_s - 1)
                # Transfer function squared
                T_sq = Pk / (P_prim * (2 * np.pi**2) / k_values**3)
                ax2.loglog(k_values, np.sqrt(np.abs(T_sq)), 
                          label=model_name, linewidth=2, alpha=0.8)
    
    ax2.set_xlabel('k [h/Mpc]', fontsize='x-large')
    ax2.set_ylabel('T(k)', fontsize='x-large')
    ax2.set_title('Transfer Function', fontsize='x-large')
    # ax2.grid(True, alpha=0.3, which='both')
    
    plt.tight_layout()
    if save_path is not None:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    # plt.show()

    return fig
