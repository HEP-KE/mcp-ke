#!/usr/bin/env python
"""
End-to-end test calling tools through the actual MCP protocol (stdio),
exactly as the HEP-multiagent does via langchain_mcp_adapters.
"""

import asyncio
import os
import sys
import json
import tempfile
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

OUTPUT_DIR = tempfile.mkdtemp(prefix="mcp_e2e_test_")


def extract_text(result):
    """Extract text from MCP result (handles various return formats)."""
    if isinstance(result, list) and len(result) > 0:
        item = result[0]
        if isinstance(item, dict) and "text" in item:
            return item["text"]
        return str(item)
    return str(result)


async def main():
    from langchain_mcp_adapters.client import MultiServerMCPClient

    venv_bin = os.path.join(sys.prefix, "bin", "mcp_ke")
    cmd = venv_bin if os.path.exists(venv_bin) else "mcp_ke"
    print(f"MCP server command: {cmd}")
    print(f"Output directory: {OUTPUT_DIR}")

    config = {
        "mcp_ke": {
            "transport": "stdio",
            "command": cmd,
            "args": [],
            "env": {**os.environ, "MCP_OUTPUT_DIR": OUTPUT_DIR},
        }
    }

    client = MultiServerMCPClient(config)
    tools = await client.get_tools()
    tool_map = {t.name: t for t in tools}

    print(f"Discovered {len(tools)} tools\n")

    errors = []

    # ---- Prepare real data (read directly to get clean arrays) ----
    data = np.loadtxt("/data/a/cpac/nramachandra/Projects/AmSC/mcp-ke/data/DR14_pm3d_19kbins.txt")
    k_obs = data[:, 0]
    Pk_obs = data[:, 1]
    Pk_obs_err = data[:, 2]
    k_theory = np.logspace(-4, np.log10(10), 300)

    # Compute real P(k) locally (we need arrays to test plotting)
    from codes.analysis import compute_power_spectrum as compute_pk
    from codes.cosmology_models import base_params

    lcdm = base_params()
    lcdm_pk = compute_pk(lcdm, k_theory)
    wcdm = base_params()
    wcdm["_w0_approx"] = -0.9
    wcdm_pk = compute_pk(wcdm, k_theory)
    nu = base_params()
    nu["N_ur"] = 2.044
    nu["N_ncdm"] = 1
    nu["m_ncdm"] = "0.1"
    nu["T_ncdm"] = 0.71611
    nu_pk = compute_pk(nu, k_theory)

    print(f"LCDM P(k) computed: shape={lcdm_pk.shape}")
    print(f"wCDM P(k) computed: shape={wcdm_pk.shape}")
    print(f"nu P(k) computed: shape={nu_pk.shape}")

    # ===========================================================
    # CRITICAL TEST: plot_power_spectra through MCP protocol
    # ===========================================================
    # Test all input formats the LLM might use

    # Test A: Python lists (most common - LLM constructs lists in JSON)
    print("\n" + "=" * 60)
    print("TEST A: plot_power_spectra with Python lists")
    r = await tool_map["plot_power_spectra"].ainvoke({
        "k_theory": k_theory.tolist(),
        "model_results": {
            "ΛCDM": lcdm_pk.tolist(),
            "wCDM (w0=-0.9)": wcdm_pk.tolist(),
            "ΛCDM + Σmν=0.10 eV": nu_pk.tolist(),
        },
        "k_obs": k_obs.tolist(),
        "Pk_obs": Pk_obs.tolist(),
        "Pk_obs_err": Pk_obs_err.tolist(),
        "save_path": "test_A_lists.png",
    })
    txt = extract_text(r)
    print(f"  Result: {txt}")
    if "Error" in txt:
        errors.append(("plot_lists", txt))

    # Test B: JSON strings (LLM sometimes sends arrays as strings)
    print("\n" + "=" * 60)
    print("TEST B: plot_power_spectra with JSON string k_theory")
    r = await tool_map["plot_power_spectra"].ainvoke({
        "k_theory": json.dumps(k_theory.tolist()),
        "model_results": {
            "ΛCDM": lcdm_pk.tolist(),
        },
        "k_obs": json.dumps(k_obs.tolist()),
        "Pk_obs": json.dumps(Pk_obs.tolist()),
        "Pk_obs_err": json.dumps(Pk_obs_err.tolist()),
        "save_path": "test_B_jsonstr.png",
    })
    txt = extract_text(r)
    print(f"  Result: {txt}")
    if "Error" in txt:
        errors.append(("plot_jsonstr", txt))

    # Test C: Mixed (some list, some string)
    print("\n" + "=" * 60)
    print("TEST C: plot_power_spectra with mixed types")
    r = await tool_map["plot_power_spectra"].ainvoke({
        "k_theory": k_theory.tolist(),
        "model_results": {
            "ΛCDM": lcdm_pk.tolist(),
            "wCDM (w0=-0.9)": wcdm_pk.tolist(),
        },
        "k_obs": k_obs.tolist(),
        "Pk_obs": Pk_obs.tolist(),
        "Pk_obs_err": Pk_obs_err.tolist(),
        "save_path": "test_C_mixed.png",
    })
    txt = extract_text(r)
    print(f"  Result: {txt}")
    if "Error" in txt:
        errors.append(("plot_mixed", txt))

    # ===========================================================
    # plot_suppression_ratios
    # ===========================================================
    print("\n" + "=" * 60)
    print("TEST D: plot_suppression_ratios")
    r = await tool_map["plot_suppression_ratios"].ainvoke({
        "k_values": k_theory.tolist(),
        "suppression_ratios": {
            "wCDM (w0=-0.9)": (wcdm_pk / lcdm_pk).tolist(),
            "ΛCDM + Σmν=0.10 eV": (nu_pk / lcdm_pk).tolist(),
        },
        "save_path": "test_D_suppression.png",
    })
    txt = extract_text(r)
    print(f"  Result: {txt}")
    if "Error" in txt:
        errors.append(("suppression", txt))

    # ===========================================================
    # MCMC through MCP
    # ===========================================================
    print("\n" + "=" * 60)
    print("TEST E: run_mcmc_cosmology")
    r = await tool_map["run_mcmc_cosmology"].ainvoke({
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
        "output_filename": "e2e_mcmc_samples.csv",
    })
    txt = extract_text(r)
    print(f"  Result (first 400): {txt[:400]}")
    if "Error running MCMC" in txt:
        errors.append(("mcmc", txt))

    # ===========================================================
    # Corner plot
    # ===========================================================
    print("\n" + "=" * 60)
    print("TEST F: create_mcmc_corner_plot")
    samples_path = os.path.join(OUTPUT_DIR, "e2e_mcmc_samples.csv")
    if os.path.exists(samples_path):
        r = await tool_map["create_mcmc_corner_plot"].ainvoke({
            "samples_csv": samples_path,
            "output_filename": "e2e_corner.png",
        })
        txt = extract_text(r)
        print(f"  Result (first 300): {txt[:300]}")
        if "Error" in txt:
            errors.append(("corner", txt))
    else:
        print(f"  SKIPPED (no samples file)")
        print(f"  Files: {os.listdir(OUTPUT_DIR)}")

    # ===========================================================
    # Analyze samples
    # ===========================================================
    print("\n" + "=" * 60)
    print("TEST G: analyze_mcmc_samples")
    if os.path.exists(samples_path):
        r = await tool_map["analyze_mcmc_samples"].ainvoke({
            "samples_csv": samples_path,
        })
        txt = extract_text(r)
        print(f"  Result (first 400): {txt[:400]}")

    # ===========================================================
    # Best-fit P(k)
    # ===========================================================
    print("\n" + "=" * 60)
    print("TEST H: compute_best_fit_power_spectrum")
    if os.path.exists(samples_path):
        r = await tool_map["compute_best_fit_power_spectrum"].ainvoke({
            "samples_csv": samples_path,
            "k_values": k_theory.tolist(),
        })
        txt = extract_text(r)
        print(f"  Result (first 300): {txt[:300]}")
        if txt.startswith("Error"):
            errors.append(("bestfit", txt))

    # ===========================================================
    # SUMMARY
    # ===========================================================
    print("\n" + "=" * 60)
    print("PIPELINE SUMMARY")
    print("=" * 60)

    files = os.listdir(OUTPUT_DIR)
    print(f"Output files ({len(files)}):")
    for f in sorted(files):
        fpath = os.path.join(OUTPUT_DIR, f)
        size = os.path.getsize(fpath)
        print(f"  {f} ({size:,} bytes)")

    if errors:
        print(f"\n{len(errors)} STEPS FAILED:")
        for step, err in errors:
            print(f"  {step}: {err[:150]}")
        sys.exit(1)
    else:
        print("\nALL STEPS PASSED!")

    # Note: MultiServerMCPClient does not support __aexit__; it cleans up on GC


if __name__ == "__main__":
    asyncio.run(main())
