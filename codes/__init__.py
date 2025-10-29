"""Implementation code for cosmology analysis tools."""

# Re-export implementations from the tools directory
import sys
import os

# Add tools directory to path for imports
_tools_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tools')
if _tools_dir not in sys.path:
    sys.path.insert(0, _tools_dir)

# Import and re-export the implementation modules
from data import load_observational_data
from cosmology_models import LCDM, nu_mass, wCDM
from analysis import compute_power_spectrum, compute_all_models, compute_suppression_ratios
from viz import plot_power_spectra, plot_suppression_ratios

__all__ = [
    "load_observational_data",
    "LCDM",
    "nu_mass",
    "wCDM",
    "compute_power_spectrum",
    "compute_all_models",
    "compute_suppression_ratios",
    "plot_power_spectra",
    "plot_suppression_ratios",
]
