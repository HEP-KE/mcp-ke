"""Agent tool for power spectrum analysis using multiagent orchestration."""

from smolagents import tool
from .llm_helper import create_openai_compatible_llm

@tool
def analyze_power_spectrum_multiagent(
    query: str,
    api_key: str,
    llm_url: str,
    model_id: str,
    output_dir: str = "./out",
    input_dir: str = "./input"
) -> str:
    """
    Analyze cosmological power spectra using a multiagent orchestration system.

    This tool orchestrates three specialized agents to perform end-to-end power spectrum analysis:

    1. **Data Agent**: Loads eBOSS DR14 Lyman-alpha forest observational data
       - Extracts k-values, P(k) measurements, and error bars
       - Saves data arrays to output directory

    2. **Modeling Agent**: Computes theoretical power spectra for cosmological models
       - Supports ΛCDM, massive neutrinos (Σmν), wCDM (dark energy)
       - Creates high-resolution theory k-grid (300 points, 0.0001-10 h/Mpc)
       - Computes P(k) predictions and suppression ratios

    3. **Viz Agent**: Creates comparison visualizations
       - Plots theoretical predictions vs observational data
       - Generates suppression ratio plots (P(k)/P_ΛCDM(k))

    The orchestrator coordinates these agents sequentially, passing file paths between them.

    REQUIREMENTS:
    - multiagent_sys package installed: pip install git+https://github.com/HEP-KE/multiagent_sys.git

    Args:
        query: Detailed analysis request describing what to analyze. Examples:
            - "Load eBOSS data, compute ΛCDM and wCDM power spectra, create comparison plot"
            - "Analyze power spectrum suppression for massive neutrino models"
            - "Compare ΛCDM with Σmν=0.10 eV model and visualize the differences"
        api_key: API key for the LLM service (required)
        llm_url: Base URL for the LLM API endpoint (required)
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
            - File paths to generated outputs (plots, data arrays) in out/ directory
            - Status of each agent's execution
            - Any error messages if steps failed

    Example:
        result = analyze_power_spectrum_multiagent(
            query="Load observational data, compute power spectra for ΛCDM and "
                  "massive neutrino models with Σmν=0.10 eV, then create a "
                  "visualization comparing them with the observations",
            api_key="your-api-key-here",
            llm_url="https://api.anthropic.com",
            model_id="claude-3-5-sonnet-20241022"
        )
    """
    try:
        from multiagent_sys import run_multiagent_system
        import os

        # Create directories if they don't exist
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(input_dir, exist_ok=True)

        # Validate LLM configuration
        try:
            create_openai_compatible_llm(api_key, llm_url, model_id)
        except ValueError as e:
            return f"LLM Configuration Error: {str(e)}"
        except ImportError as e:
            return f"Installation Error: {str(e)}"

        # Note: multiagent_sys expects 'out/' and 'input/' in current working directory
        # If custom directories are specified, we'll need to handle that
        if output_dir != "./out" or input_dir != "./input":
            return (f"Warning: Custom directories not yet supported by multiagent_sys. "
                    f"Please use default './out' and './input' directories for now.")

        # Run the multiagent system
        result = run_multiagent_system(
            query=query,
            api_key=api_key,
            llm_url=llm_url,
            model_id=model_id
        )

        return str(result)

    except ImportError as e:
        return (f"Error: Could not import multiagent_sys. Please install it with:\n"
                f"pip install git+https://github.com/HEP-KE/multiagent_sys.git\n"
                f"Details: {e}")
    except Exception as e:
        import traceback
        return f"Error running power spectrum analysis: {str(e)}\n{traceback.format_exc()}"
