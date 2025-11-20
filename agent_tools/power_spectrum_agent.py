"""Power Spectrum Analysis Agent - Multi-agent orchestrator for cosmology analysis."""

import os
from smolagents import CodeAgent, AgentLogger, LogLevel, tool
from smolagents.default_tools import FinalAnswerTool
from .llm_helper import create_openai_compatible_llm

# Import MCP tools directly
from tools import (
    load_observational_data,
    create_theory_k_grid,
    LCDM, nu_mass, wCDM,
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
    """Create the data agent for loading observational data."""
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
    """Create the modeling agent for computing power spectra."""
    return CodeAgent(
        tools=[
            create_theory_k_grid, LCDM, nu_mass, wCDM,
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
    """Create the visualization agent for creating plots."""
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
    """Create the orchestrator agent that coordinates all sub-agents."""
    # Create separate model instances for each sub-agent to avoid context sharing
    data_model = create_openai_compatible_llm(api_key, llm_url, model_id)
    modeling_model = create_openai_compatible_llm(api_key, llm_url, model_id)
    viz_model = create_openai_compatible_llm(api_key, llm_url, model_id)

    # Create the sub-agents
    data_agent = create_data_agent(data_model)
    modeling_agent = create_modeling_agent(modeling_model)
    viz_agent = create_viz_agent(viz_model)

    # Create the orchestrator
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


@tool
def power_spectrum_agent(
    query: str,
    api_key: str,
    llm_url: str,
    model_id: str,
    output_dir: str = "./out",
    input_dir: str = "./input"
) -> str:
    """
    Power spectrum analysis using multi-agent orchestration.

    This agent orchestrates three specialized agents for end-to-end power spectrum analysis:

    1. **Data Agent**: Loads eBOSS DR14 Lyman-alpha forest observational data
    2. **Modeling Agent**: Computes theoretical power spectra (ΛCDM, massive neutrinos, wCDM)
    3. **Viz Agent**: Creates comparison visualizations

    The orchestrator coordinates these agents sequentially, passing file paths between them.

    Args:
        query: Analysis request describing what to analyze. Examples:
            - "Load eBOSS data, compute ΛCDM and wCDM power spectra, create comparison plot"
            - "Analyze power spectrum suppression for massive neutrino models"
            - "Compare ΛCDM with Σmν=0.10 eV model and visualize the differences"
        api_key: API key for LLM service (required)
        llm_url: Base URL for LLM API endpoint (required)
            Examples:
            - Anthropic: "https://api.anthropic.com"
            - Google Gemini: "https://generativelanguage.googleapis.com/v1beta/openai/"
            - OpenAI: "https://api.openai.com/v1"
        model_id: Model identifier to use (required)
            Examples:
            - Anthropic: "claude-3-5-sonnet-20241022"
            - Google: "gemini-2.0-flash-exp"
            - OpenAI: "gpt-4"
        output_dir: Directory for output files (default: "./out")
        input_dir: Directory containing input data (default: "./input")

    Returns:
        str: Orchestrator's response containing:
            - Summary of analysis performed
            - File paths to generated outputs (plots, data arrays) in output directory
            - Status of each agent's execution
            - Any error messages if steps failed

    Example:
        result = power_spectrum_agent(
            query="Load eBOSS data, compute ΛCDM and wCDM models, create visualization",
            api_key="your-api-key",
            llm_url="https://api.anthropic.com",
            model_id="claude-3-5-sonnet-20241022"
        )
    """
    try:
        # Create output and input directories
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(input_dir, exist_ok=True)

        # Save original directory and change to output directory for agent execution
        original_dir = os.getcwd()

        try:
            # Create the LLM model
            model = create_openai_compatible_llm(api_key, llm_url, model_id)
        except ValueError as e:
            return f"LLM Configuration Error: {str(e)}"
        except ImportError as e:
            return f"Installation Error: {str(e)}"

        # Create the orchestrator with all sub-agents
        orchestrator = create_orchestrator(model, api_key, llm_url, model_id)

        # Run the orchestrator
        result = orchestrator.run(query)

        return str(result)

    except Exception as e:
        import traceback
        return f"Error running power spectrum agent: {str(e)}\n{traceback.format_exc()}"
