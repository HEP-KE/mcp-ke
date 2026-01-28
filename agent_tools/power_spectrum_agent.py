import os
from smolagents import CodeAgent, AgentLogger, LogLevel, tool
from smolagents.default_tools import FinalAnswerTool
from .llm_helper import create_openai_compatible_llm

from tools import (
    load_observational_data,
    create_theory_k_grid,
    get_lcdm_params, get_nu_mass_params, get_wcdm_params,
    compute_power_spectrum,
    compute_all_models,
    compute_suppression_ratios,
    plot_power_spectra,
    plot_suppression_ratios,
    save_array, load_array,
    save_dict, load_dict,
    list_agent_files
)


def create_data_agent(model):
    return CodeAgent(
        tools=[load_observational_data, save_array, save_dict],
        model=model,
        max_steps=20,
        verbosity_level=1,
        additional_authorized_imports=["numpy", "matplotlib", "pandas", "json"],
        code_block_tags="markdown",
        name="data_agent",
        description="Loads observational data from eBOSS DR14 Lyman-alpha forest.",
        instructions="""You must use your existing tools over writing custom code.

In your final_answer, include all file paths returned by save_array() and save_dict()."""
    )


def create_modeling_agent(model):
    return CodeAgent(
        tools=[
            create_theory_k_grid, get_lcdm_params, get_nu_mass_params, get_wcdm_params,
            compute_power_spectrum, compute_all_models, compute_suppression_ratios,
            load_array, save_array, load_dict, save_dict, list_agent_files
        ],
        model=model,
        max_steps=40,
        verbosity_level=1,
        additional_authorized_imports=["numpy", "matplotlib", "json"],
        code_block_tags="markdown",
        name="modeling_agent",
        description="Computes linear P(k) predictions for ΛCDM, massive neutrinos, and wCDM models.",
        instructions="""You must use your existing tools over writing custom code.

Your task description will contain file paths from previous agents - use load_array() and load_dict() to load them.

In your final_answer, include all file paths returned by save_array() and save_dict()."""
    )


def create_viz_agent(model):
    return CodeAgent(
        tools=[plot_power_spectra, plot_suppression_ratios, load_array, load_dict, list_agent_files],
        model=model,
        max_steps=30,
        verbosity_level=1,
        additional_authorized_imports=["numpy", "matplotlib", "json"],
        code_block_tags="markdown",
        name="viz_agent",
        description="Creates visualizations comparing theoretical P(k) predictions with observations.",
        instructions="""Use your existing tools over writing custom code.

Your task description will contain file paths from previous agents - use load_array() and load_dict() to load them.

In your final_answer, include all plot file paths."""
    )


def create_orchestrator(model, api_key, llm_url, model_id):
    data_model = create_openai_compatible_llm(api_key, llm_url, model_id)
    modeling_model = create_openai_compatible_llm(api_key, llm_url, model_id)
    viz_model = create_openai_compatible_llm(api_key, llm_url, model_id)

    data_agent = create_data_agent(data_model)
    modeling_agent = create_modeling_agent(modeling_model)
    viz_agent = create_viz_agent(viz_model)

    return CodeAgent(
        name="orchestrator_agent",
        tools=[],
        model=model,
        managed_agents=[data_agent, modeling_agent, viz_agent],
        max_steps=50,
        verbosity_level=1,
        code_block_tags="markdown",
        instructions="""Coordinate agents by calling them sequentially.

CRITICAL WORKFLOW for power spectrum analysis:

1. Data Agent:
   - Ask data_agent to load observational data
   - Extract file paths for observational k, P(k), and errors from response

2. Modeling Agent:
   - Ask modeling_agent to compute theoretical power spectra for requested models
   - DO NOT pass observational k-values to modeling_agent!
   - The modeling_agent will create its own theory k-grid (300 points, 0.0001-10 h/Mpc)
   - This is different from observational k-bins (only 19 points, 0.2-2.5 h/Mpc)
   - Extract file paths for theory k-grid and model results from response

3. Viz Agent:
   - Pass BOTH file paths to viz_agent:
     a) Observational data files (k_obs, Pk_obs, errors) from data_agent
     b) Theory data files (k_theory, model_results) from modeling_agent
   - viz_agent needs both to create comparison plots

You MUST extract and pass file paths between agents. Never pass raw data arrays."""
    )


POWER_SPECTRUM_AGENT_MAX_STEPS = 50

@tool
def power_spectrum_agent(query: str) -> str:
    """
    Autonomous power spectrum analysis agent that orchestrates data, modeling, and visualization.

    Use this instead of individual cosmology tools when you need:
    - End-to-end analysis: load observations → compute theory predictions → create comparison plots
    - Automatic coordination between data loading, model computation, and visualization
    - Complex multi-model comparisons (ΛCDM vs neutrino vs wCDM)
    - File management between analysis stages handled automatically

    Args:
        query: Analysis request (e.g., "Compare ΛCDM with massive neutrino models using eBOSS data")

    Returns:
        str: Analysis summary with file paths to generated plots and data.
    """
    api_key = os.environ.get("LLM_API_KEY")
    llm_url = os.environ.get("LLM_URL")
    model_id = os.environ.get("LLM_MODEL")

    missing = [k for k, v in [("LLM_API_KEY", api_key), ("LLM_URL", llm_url), ("LLM_MODEL", model_id)] if not v]
    if missing:
        return f"Error: Missing environment variables: {', '.join(missing)}. Set these when configuring the MCP server."

    try:
        try:
            model = create_openai_compatible_llm(api_key, llm_url, model_id)
        except (ValueError, ImportError) as e:
            return f"LLM Setup Error: {str(e)}"

        orchestrator = create_orchestrator(model, api_key, llm_url, model_id)
        result = orchestrator.run(query)

        return str(result)

    except Exception as e:
        import traceback
        return f"Error running power spectrum agent: {str(e)}\n{traceback.format_exc()}"
