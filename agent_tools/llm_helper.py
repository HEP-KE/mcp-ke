"""Helper functions for creating LLM instances for agent tools."""


def create_openai_compatible_llm(api_key: str, llm_url: str, model_id: str):
    """
    Create and return an OpenAI-compatible LLM instance for agent tools.

    This helper function creates a model instance from any LLM service that provides
    an OpenAI-compatible chat API endpoint. This includes Anthropic, Google Gemini,
    OpenAI, and other providers that support the OpenAI chat format.

    Args:
        api_key: API key for the LLM service (required)
        llm_url: Base URL for the LLM API endpoint
            Examples:
            - Anthropic: "https://api.anthropic.com"
            - Google Gemini: "https://generativelanguage.googleapis.com/v1beta/openai/"
            - OpenAI: "https://api.openai.com/v1"
        model_id: Model identifier
            Examples:
            - Anthropic: "claude-3-5-sonnet-20241022"
            - Google: "gemini-2.0-flash-exp"
            - OpenAI: "gpt-4"

    Returns:
        Model instance configured with the provided settings

    Raises:
        ValueError: If api_key is empty or None
        ImportError: If multiagent_sys package is not installed

    Example:
        model = create_openai_compatible_llm(
            api_key="your-api-key",
            llm_url="https://api.anthropic.com",
            model_id="claude-3-5-sonnet-20241022"
        )
    """
    # Validate required API key
    if not api_key:
        raise ValueError(
            "api_key is required for agent tools.\n"
            "Please provide a valid API key."
        )

    # Validate other required parameters
    if not llm_url:
        raise ValueError("llm_url is required for agent tools.")

    if not model_id:
        raise ValueError("model_id is required for agent tools.")

    try:
        from multiagent_sys.llms.remote_llms import create_model
    except ImportError as e:
        raise ImportError(
            "multiagent_sys package is required for agent tools.\n"
            "Install it with:\n"
            "  pip install git+https://github.com/HEP-KE/multiagent_sys.git\n"
            f"\nDetails: {e}"
        )

    # Create and return the model
    return create_model(api_key, llm_url, model_id)
