#!/usr/bin/env python
"""
Full end-to-end pipeline test that replicates what the MCP server does.

Calls tools_dict[name](**arguments) and str(result) exactly like mcp_server.py:call_tool().
This simulates the full demo_mcmc.ipynb workflow:
  1. load_observational_data
  2. create_theory_k_grid
  3. compute P(k) for LCDM, wCDM, LCDM+nu
  4. plot_power_spectra
  5. run_mcmc_cosmology
  6. create_mcmc_corner_plot
  7. analyze_mcmc_samples
  8. compute_best_fit_power_spectrum
"""

import sys
import os
import json
import tempfile
from pathlib import Path

# Add parent directory to path (same as mcp_server.py)
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set output directory
OUTPUT_DIR = tempfile.mkdtemp(prefix="mcp_pipeline_test_")
os.environ["MCP_OUTPUT_DIR"] = OUTPUT_DIR
print(f"Output directory: {OUTPUT_DIR}")

# ---- Discover tools exactly like mcp_server.py ----
from mcp_server import discover_tools

tools_dict = discover_tools()
print(f"\nDiscovered {len(tools_dict)} tools:")
for name in sorted(tools_dict.keys()):
    print(f"  - {name}")


def call_tool(name, arguments):
    """Replicate mcp_server.py call_tool() exactly."""
    if name not in tools_dict:
        return f"Error: Tool '{name}' not found"
    try:
        result = tools_dict[name](**arguments)
        return str(result)
    except Exception as e:
        return f"Error: {e}"


# =============================================================
# STEP 1: Load observational data
# =============================================================
print("\n" + "=" * 60)
print("STEP 1: load_observational_data")
print("=" * 60)

result = call_tool("load_observational_data", {
    "filepath": "/data/a/cpac/nramachandra/Projects/AmSC/mcp-ke/data/DR14_pm3d_19kbins.txt"
})
print(f"Result type: {type(result)}")
print(f"Result (first 300 chars): {result[:300]}")

# Parse the result - it returns a tuple of 3 arrays
# The MCP server returns str(result), so the LLM gets a string representation.
# The LLM then needs to extract data or use file references.
# Let's call the tool directly to get the actual objects:
obs_result = tools_dict["load_observational_data"](
    filepath="/data/a/cpac/nramachandra/Projects/AmSC/mcp-ke/data/DR14_pm3d_19kbins.txt"
)
print(f"\nDirect call result type: {type(obs_result)}")
k_obs, Pk_obs, Pk_obs_err = obs_result
print(f"k_obs shape: {k_obs.shape}, dtype: {k_obs.dtype}")
print(f"Pk_obs shape: {Pk_obs.shape}")
print(f"Pk_obs_err shape: {Pk_obs_err.shape}")

# Save arrays for later steps (like the LLM would via save_array)
for name_arr, arr in [("k_obs", k_obs), ("Pk_obs", Pk_obs), ("Pk_obs_err", Pk_obs_err)]:
    r = call_tool("save_array", {"array": arr.tolist(), "filename": f"{name_arr}.npy"})
    print(f"save_array({name_arr}): {r}")


# =============================================================
# STEP 2: Create theory k-grid
# =============================================================
print("\n" + "=" * 60)
print("STEP 2: create_theory_k_grid")
print("=" * 60)

result_str = call_tool("create_theory_k_grid", {})
print(f"Result (first 200 chars): {result_str[:200]}")

# Get actual array
k_theory = tools_dict["create_theory_k_grid"]()
print(f"k_theory shape: {k_theory.shape}, range: [{k_theory.min():.6f}, {k_theory.max():.6f}]")

# Save
r = call_tool("save_array", {"array": k_theory.tolist(), "filename": "k_theory.npy"})
print(f"save_array(k_theory): {r}")


# =============================================================
# STEP 3: Get model parameters and compute P(k)
# =============================================================
print("\n" + "=" * 60)
print("STEP 3: Compute P(k) for LCDM, wCDM, LCDM+nu")
print("=" * 60)

# Get LCDM params
lcdm_params_str = call_tool("get_lcdm_params", {})
print(f"LCDM params: {lcdm_params_str[:200]}")

# Get wCDM params
wcdm_params_str = call_tool("get_wcdm_params", {})
print(f"wCDM params: {wcdm_params_str[:200]}")

# Get nu_mass params
nu_params_str = call_tool("get_nu_mass_params", {})
print(f"nu_mass params: {nu_params_str[:200]}")

# Compute power spectra - pass k_theory as a list (like JSON)
lcdm_params = tools_dict["get_lcdm_params"]()
wcdm_params = tools_dict["get_wcdm_params"]()
nu_params = tools_dict["get_nu_mass_params"]()

print("\nComputing LCDM P(k)...")
Pk_lcdm_result = call_tool("compute_power_spectrum", {
    "params": lcdm_params,
    "k_values": k_theory.tolist()
})
print(f"LCDM P(k) result (first 200): {Pk_lcdm_result[:200]}")
Pk_lcdm = tools_dict["compute_power_spectrum"](lcdm_params, k_theory)

print("\nComputing wCDM P(k)...")
Pk_wcdm_result = call_tool("compute_power_spectrum", {
    "params": wcdm_params,
    "k_values": k_theory.tolist()
})
print(f"wCDM P(k) result (first 200): {Pk_wcdm_result[:200]}")
Pk_wcdm = tools_dict["compute_power_spectrum"](wcdm_params, k_theory)

print("\nComputing nu_mass P(k)...")
Pk_nu_result = call_tool("compute_power_spectrum", {
    "params": nu_params,
    "k_values": k_theory.tolist()
})
print(f"nu_mass P(k) result (first 200): {Pk_nu_result[:200]}")
Pk_nu = tools_dict["compute_power_spectrum"](nu_params, k_theory)

import numpy as np
for name_pk, pk_val in [("Pk_lcdm", Pk_lcdm), ("Pk_wcdm", Pk_wcdm), ("Pk_nu", Pk_nu)]:
    if isinstance(pk_val, np.ndarray):
        print(f"  {name_pk}: shape={pk_val.shape}, range=[{pk_val.min():.4e}, {pk_val.max():.4e}]")
    else:
        print(f"  {name_pk}: {pk_val[:200]}")


# =============================================================
# STEP 4: Plot power spectra (THE CRITICAL FAILURE POINT)
# =============================================================
print("\n" + "=" * 60)
print("STEP 4: plot_power_spectra (critical test)")
print("=" * 60)

# Test A: The way the LLM ACTUALLY calls it - everything as JSON-serializable types
# The LLM sends k_theory as a list, model_results as a dict with list values
print("\n--- Test A: All inputs as Python lists (from JSON) ---")
plot_args_lists = {
    "k_theory": k_theory.tolist(),
    "model_results": {
        "ΛCDM": Pk_lcdm.tolist() if isinstance(Pk_lcdm, np.ndarray) else Pk_lcdm,
        "wCDM (w0=-0.9)": Pk_wcdm.tolist() if isinstance(Pk_wcdm, np.ndarray) else Pk_wcdm,
        "ΛCDM + Σmν=0.10 eV": Pk_nu.tolist() if isinstance(Pk_nu, np.ndarray) else Pk_nu,
    },
    "k_obs": k_obs.tolist(),
    "Pk_obs": Pk_obs.tolist(),
    "Pk_obs_err": Pk_obs_err.tolist(),
    "save_path": "test_plot_lists.png",
}
result_a = call_tool("plot_power_spectra", plot_args_lists)
print(f"Result: {result_a}")

# Test B: k_theory as JSON string (common LLM behavior)
print("\n--- Test B: k_theory as JSON string ---")
plot_args_jsonstr = {
    "k_theory": json.dumps(k_theory.tolist()),
    "model_results": {
        "ΛCDM": Pk_lcdm.tolist() if isinstance(Pk_lcdm, np.ndarray) else Pk_lcdm,
    },
    "k_obs": json.dumps(k_obs.tolist()),
    "Pk_obs": json.dumps(Pk_obs.tolist()),
    "Pk_obs_err": json.dumps(Pk_obs_err.tolist()),
    "save_path": "test_plot_jsonstr.png",
}
result_b = call_tool("plot_power_spectra", plot_args_jsonstr)
print(f"Result: {result_b}")

# Test C: numpy arrays directly
print("\n--- Test C: numpy arrays directly ---")
plot_args_numpy = {
    "k_theory": k_theory,
    "model_results": {
        "ΛCDM": Pk_lcdm,
        "wCDM (w0=-0.9)": Pk_wcdm,
        "ΛCDM + Σmν=0.10 eV": Pk_nu,
    },
    "k_obs": k_obs,
    "Pk_obs": Pk_obs,
    "Pk_obs_err": Pk_obs_err,
    "save_path": "test_plot_numpy.png",
}
result_c = call_tool("plot_power_spectra", plot_args_numpy)
print(f"Result: {result_c}")


# Test D: Simulate what the LLM sees and sends back
# After calling str(result) on arrays, the LLM gets string representations.
# It might copy/paste these back. Let's simulate this.
print("\n--- Test D: str() representations (what LLM might echo back) ---")
# This is the nightmare scenario - LLM gets str(ndarray) and passes it back
k_str = str(k_theory.tolist()[:5])  # First 5 elements as string
print(f"  k_str sample: {k_str}")


# =============================================================
# STEP 5: Plot suppression ratios
# =============================================================
print("\n" + "=" * 60)
print("STEP 5: plot_suppression_ratios")
print("=" * 60)

if isinstance(Pk_lcdm, np.ndarray) and isinstance(Pk_wcdm, np.ndarray):
    supp_ratios = {
        "wCDM (w0=-0.9)": (Pk_wcdm / Pk_lcdm).tolist(),
        "ΛCDM + Σmν=0.10 eV": (Pk_nu / Pk_lcdm).tolist() if isinstance(Pk_nu, np.ndarray) else [],
    }
    result_supp = call_tool("plot_suppression_ratios", {
        "k_values": k_theory.tolist(),
        "suppression_ratios": supp_ratios,
        "save_path": "test_suppression.png",
    })
    print(f"Result: {result_supp}")
else:
    print("SKIPPED: P(k) computation returned errors")


# =============================================================
# STEP 6: Run MCMC (small run)
# =============================================================
print("\n" + "=" * 60)
print("STEP 6: run_mcmc_cosmology (small run)")
print("=" * 60)

mcmc_args = {
    "param_bounds": [
        {"name": "A_s", "min": 1.5e-9, "max": 3.0e-9},
        {"name": "n_s", "min": 0.90, "max": 1.05},
    ],
    "k_obs": k_obs.tolist(),
    "Pk_obs": Pk_obs.tolist(),
    "Pk_obs_err": Pk_obs_err.tolist(),
    "nwalkers": 8,
    "nburn": 5,
    "nrun": 10,
    "save_samples": True,
    "output_filename": "test_mcmc_samples.csv",
}

result_mcmc = call_tool("run_mcmc_cosmology", mcmc_args)
print(f"MCMC result (first 500): {result_mcmc[:500]}")

# Also test with JSON string arrays
print("\n--- MCMC with JSON string arrays ---")
mcmc_args_json = {
    "param_bounds": json.dumps([
        {"name": "A_s", "min": 1.5e-9, "max": 3.0e-9},
        {"name": "n_s", "min": 0.90, "max": 1.05},
    ]),
    "k_obs": json.dumps(k_obs.tolist()),
    "Pk_obs": json.dumps(Pk_obs.tolist()),
    "Pk_obs_err": json.dumps(Pk_obs_err.tolist()),
    "nwalkers": 8,
    "nburn": 5,
    "nrun": 10,
    "save_samples": True,
    "output_filename": "test_mcmc_samples_json.csv",
}
result_mcmc_json = call_tool("run_mcmc_cosmology", mcmc_args_json)
print(f"MCMC (JSON) result (first 500): {result_mcmc_json[:500]}")


# =============================================================
# STEP 7: Corner plot
# =============================================================
print("\n" + "=" * 60)
print("STEP 7: create_mcmc_corner_plot")
print("=" * 60)

# Find the samples CSV
samples_path = os.path.join(OUTPUT_DIR, "test_mcmc_samples.csv")
if os.path.exists(samples_path):
    corner_args = {
        "samples_csv": samples_path,
        "param_labels": {"A_s": r"A_s", "n_s": r"n_s"},
        "output_filename": "test_corner.png",
    }
    result_corner = call_tool("create_mcmc_corner_plot", corner_args)
    print(f"Corner result (first 300): {result_corner[:300]}")
else:
    print(f"SKIPPED: No samples file at {samples_path}")
    # Check what files exist
    print(f"Files in output dir: {os.listdir(OUTPUT_DIR)}")


# =============================================================
# STEP 8: Analyze samples
# =============================================================
print("\n" + "=" * 60)
print("STEP 8: analyze_mcmc_samples")
print("=" * 60)

if os.path.exists(samples_path):
    result_analyze = call_tool("analyze_mcmc_samples", {"samples_csv": samples_path})
    print(f"Analysis result (first 500): {result_analyze[:500]}")
else:
    print("SKIPPED: No samples file")


# =============================================================
# STEP 9: Best-fit power spectrum
# =============================================================
print("\n" + "=" * 60)
print("STEP 9: compute_best_fit_power_spectrum")
print("=" * 60)

if os.path.exists(samples_path):
    bestfit_args = {
        "samples_csv": samples_path,
        "k_values": k_theory.tolist(),
    }
    result_bestfit = call_tool("compute_best_fit_power_spectrum", bestfit_args)
    print(f"Best-fit result (first 300): {result_bestfit[:300]}")

    # Also test with JSON string
    bestfit_args_json = {
        "samples_csv": samples_path,
        "k_values": json.dumps(k_theory.tolist()),
    }
    result_bestfit_json = call_tool("compute_best_fit_power_spectrum", bestfit_args_json)
    print(f"Best-fit (JSON) result (first 300): {result_bestfit_json[:300]}")
else:
    print("SKIPPED: No samples file")


# =============================================================
# SUMMARY
# =============================================================
print("\n" + "=" * 60)
print("PIPELINE SUMMARY")
print("=" * 60)

files = os.listdir(OUTPUT_DIR)
print(f"Output files ({len(files)}):")
for f in sorted(files):
    fpath = os.path.join(OUTPUT_DIR, f)
    size = os.path.getsize(fpath)
    print(f"  {f} ({size:,} bytes)")

# Check for errors
errors = []
for step, result in [
    ("load_obs", result_str if 'result_str' in dir() else ""),
    ("plot_lists", result_a),
    ("plot_jsonstr", result_b),
    ("plot_numpy", result_c),
    ("suppression", result_supp if 'result_supp' in dir() else "SKIPPED"),
    ("mcmc", result_mcmc),
    ("mcmc_json", result_mcmc_json),
    ("corner", result_corner if 'result_corner' in dir() else "SKIPPED"),
    ("analyze", result_analyze if 'result_analyze' in dir() else "SKIPPED"),
    ("bestfit", result_bestfit if 'result_bestfit' in dir() else "SKIPPED"),
]:
    if result.startswith("Error"):
        errors.append((step, result))
        print(f"  FAILED: {step}: {result[:100]}")

if not errors:
    print("\n  ALL STEPS PASSED!")
else:
    print(f"\n  {len(errors)} STEPS FAILED")
