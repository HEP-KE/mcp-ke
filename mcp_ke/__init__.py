"""MCP-KE: Cosmology analysis tools."""

from tools import (
    load_observational_data,
    create_theory_k_grid,
    get_lcdm_params,
    get_nu_mass_params,
    get_wcdm_params,
    compute_power_spectrum,
    compute_all_models,
    compute_suppression_ratios,
    plot_power_spectra,
    plot_suppression_ratios,
    list_agent_files,
    save_array,
    load_array,
    save_dict,
    load_dict,
)

from agent_tools import arxiv_agent, power_spectrum_agent
from agent_tools.arxiv_agent import (
    search_arxiv,
    download_arxiv_paper,
    download_full_arxiv_paper,
    read_text_file,
    list_files,
)

__all__ = [
    "load_observational_data",
    "create_theory_k_grid",
    "get_lcdm_params",
    "get_nu_mass_params",
    "get_wcdm_params",
    "compute_power_spectrum",
    "compute_all_models",
    "compute_suppression_ratios",
    "plot_power_spectra",
    "plot_suppression_ratios",
    "list_agent_files",
    "save_array",
    "load_array",
    "save_dict",
    "load_dict",
    "arxiv_agent",
    "power_spectrum_agent",
    "search_arxiv",
    "download_arxiv_paper",
    "download_full_arxiv_paper",
    "read_text_file",
    "list_files",
]
