# COMMENTED OUT - these tools use hidden default parameters
# Replaced by explicit primitive parameters in compute_power_spectrum

# import json
# from smolagents import tool
# from mcp_utils.session import get_session
#
#
# @tool
# def get_lcdm_params() -> str:
#     """
#     Flat ΛCDM baseline (cold dark matter + cosmological constant).
#     """
#     from codes.cosmology_models import LCDM as LCDM_model
#     params = LCDM_model()
#     session = get_session()
#     dataset_name, info = session.load_dataset(params, name="lcdm_params")
#     return json.dumps({
#         "status": "success",
#         "dataset": dataset_name,
#         "type": "dict",
#         "keys": info.columns,
#         "usage": f"Use '{dataset_name}' as params_name in compute_power_spectrum."
#     }, indent=2)
#
# @tool
# def get_nu_mass_params(sum_mnu_eV: float = 0.10, N_species: int = 1) -> str:
#     """
#     ΛCDM + massive neutrinos.
#     """
#     from codes.cosmology_models import nu_mass as nu_mass_model
#     params = nu_mass_model(sum_mnu_eV, N_species)
#     session = get_session()
#     dataset_name, info = session.load_dataset(params, name=f"nu_mass_{sum_mnu_eV}eV_params")
#     return json.dumps({
#         "status": "success",
#         "dataset": dataset_name,
#         "type": "dict",
#         "keys": info.columns,
#         "usage": f"Use '{dataset_name}' as params_name in compute_power_spectrum."
#     }, indent=2)
#
# @tool
# def get_wcdm_params(w0: float = -0.9) -> str:
#     """
#     Dark energy with constant equation of state parameter w0.
#     """
#     from codes.cosmology_models import wCDM as wCDM_model
#     params = wCDM_model(w0)
#     session = get_session()
#     dataset_name, info = session.load_dataset(params, name=f"wcdm_w0{w0}_params")
#     return json.dumps({
#         "status": "success",
#         "dataset": dataset_name,
#         "type": "dict",
#         "keys": info.columns,
#         "usage": f"Use '{dataset_name}' as params_name in compute_power_spectrum."
#     }, indent=2)