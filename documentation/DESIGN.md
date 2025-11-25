# MCP-KE Design Document

## Overview

**MCP-KE** (Model Context Protocol - Knowledge Engineering) is an MCP server that provides AI-powered tools for cosmological data analysis. It implements the **"tools-as-agents"** pattern, exposing both simple computational tools and complex multi-agent workflows through a uniform MCP interface.

## Motivation

### The Problem

Modern cosmology analysis requires:
1. **Domain expertise**: Understanding CLASS (Cosmic Linear Anisotropy Solving System), power spectrum analysis, observational data formats
2. **Multi-step workflows**: Load data → compute models → analyze results → create visualizations
3. **Integration complexity**: Connecting scientific computing libraries with AI agents

Traditional approaches require either:
- Writing extensive custom code for each analysis task
- Deep knowledge of cosmology software and Python scientific stack
- Manual orchestration of multi-step analysis pipelines

### The Solution

MCP-KE provides a **tool server** that:
- Exposes 23 specialized tools via MCP protocol
- Allows any MCP client (Claude Desktop, custom agents) to perform cosmology analysis
- Encapsulates domain expertise in reusable tool functions
- Provides both **atomic tools** (simple functions) and **agent tools** (multi-agent workflows)

## Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                      MCP Client Layer                        │
│  (Claude Desktop, custom agentic systems, etc.)             │
└────────────────────────┬────────────────────────────────────┘
                         │ MCP Protocol (stdio)
┌────────────────────────▼────────────────────────────────────┐
│                    mcp_server.py                             │
│  • Auto-discovers @tool decorated functions                 │
│  • Converts to MCP Tool objects with JSON schemas           │
│  • Handles tool execution and error handling                │
└────────────┬───────────────────────────────┬────────────────┘
             │                               │
    ┌────────▼────────┐           ┌─────────▼──────────┐
    │  Domain Tools   │           │   Agent Tools      │
    │   (tools/)      │           │  (agent_tools/)    │
    │                 │           │                    │
    │  16 tools for:  │           │  2 orchestrators:  │
    │  • Data loading │           │  • power_spectrum  │
    │  • Cosmology    │           │  • arxiv_agent     │
    │    models       │           │                    │
    │  • Power        │           │  Each runs its own │
    │    spectrum     │           │  multi-agent system│
    │    computation  │           │  internally        │
    │  • Plotting     │           │                    │
    └─────────────────┘           └────────────────────┘
```

### Core Design Principles

1. **Uniform Tool Interface**: Everything exposed as MCP tools, whether simple function or complex multi-agent workflow
2. **Auto-Discovery**: Tools are automatically discovered via `@tool` decorator - no manual registration
3. **Composability**: Simple tools can be composed by agents; agent tools handle complex workflows
4. **Separation of Concerns**: Domain logic (`codes/`) separate from tool wrappers (`tools/`, `agent_tools/`)
5. **Stateless Execution**: Each tool call is independent; state managed through file I/O

## Component Architecture

### 1. MCP Server (`mcp_server.py`)

**Purpose**: Bridge between MCP protocol and Python tool functions

**Key Mechanisms**:

```python
# Tool Discovery (lines 18-50)
def discover_tools() -> dict[str, callable]:
    """
    Walks through tools/ and agent_tools/ packages
    Finds all @tool decorated functions
    Returns dict mapping tool names to callables
    """
```

The discovery process:
1. Uses `pkgutil.walk_packages()` to traverse `tools/` and `agent_tools/`
2. Uses `inspect.getmembers()` to find decorated functions
3. Checks for `__wrapped__` or `name` attributes (smolagents @tool pattern)
4. Builds tool registry automatically

```python
# MCP Tool Schema Builder (lines 53-103)
def build_mcp_tool(name: str, func: callable) -> Tool:
    """
    Converts Python function to MCP Tool with JSON schema
    Extracts: docstring, parameters, type annotations
    Generates: MCP-compliant tool description
    """
```

**MCP Endpoints**:
- `@app.list_tools()` (line 119): Returns all discovered tools with schemas
- `@app.call_tool()` (line 126): Executes tool and returns result as TextContent

**Communication**: Runs on stdio (line 160) - stdin/stdout pipes managed by MCP client

### 2. Domain Tools (`tools/`)

**Purpose**: Atomic operations for cosmology analysis

**Categories**:

#### Data Tools
- `load_observational_data`: Load eBOSS DR14 Lyman-alpha forest data
- `create_theory_k_grid`: Generate 300-point logarithmic k-grid (0.0001-10 h/Mpc)

#### Model Parameter Tools
- `LCDM()`: Returns Planck 2018 baseline cosmology parameters
- `nu_mass(sum_mnu_eV, N_species)`: ΛCDM + massive neutrinos
- `wCDM(w0)`: Dark energy with constant equation of state

Each returns a `dict` of CLASS parameters ready for computation.

#### Analysis Tools
- `compute_power_spectrum(params, k_values)`: Single model P(k) via CLASS
- `compute_all_models(k_values, models)`: Batch compute multiple models
- `compute_suppression_ratios(model_results, k_values, reference_model)`: P(k)/P_ref(k)

#### Visualization Tools
- `plot_power_spectra(k_theory, model_results, k_obs, Pk_obs, σPk_obs)`: Two-panel comparison plot
- `plot_suppression_ratios(k_values, suppression_ratios)`: Suppression ratio plot

#### Helper Tools
- `save_array`, `load_array`: NumPy array persistence
- `save_dict`, `load_dict`: JSON dict persistence
- `list_agent_files`: List files in output directory

**Design Pattern**:
```python
@tool
def tool_name(param: type) -> return_type:
    """
    Detailed docstring (becomes MCP tool description)

    Args:
        param: Description (becomes JSON schema parameter description)

    Returns:
        Description (helps clients understand return values)
    """
    from codes.module import implementation
    return implementation(param)
```

**Thin Wrapper Philosophy**: Tools are lightweight wrappers around `codes/` implementations

### 3. Agent Tools (`agent_tools/`)

**Purpose**: Multi-agent workflows exposed as single tools

#### `power_spectrum_agent`

**Architecture**: 4-agent hierarchical system

```
power_spectrum_agent(query, api_key, llm_url, model_id)
    │
    ├─► orchestrator_agent (coordinates workflow)
    │       │
    │       ├─► data_agent
    │       │   Tools: [load_observational_data, save_array, save_dict]
    │       │   Task: Load eBOSS DR14 data, save to files
    │       │   Returns: File paths to k_obs, Pk_obs, errors
    │       │
    │       ├─► modeling_agent
    │       │   Tools: [LCDM, nu_mass, wCDM, compute_power_spectrum,
    │       │          compute_all_models, compute_suppression_ratios,
    │       │          load_array, save_array, load_dict, save_dict]
    │       │   Task: Compute theoretical P(k) for requested models
    │       │   Returns: File paths to k_theory, model_results
    │       │
    │       └─► viz_agent
    │           Tools: [plot_power_spectra, plot_suppression_ratios,
    │                  load_array, load_dict]
    │           Task: Create comparison visualizations
    │           Returns: File paths to plot PNG files
    │
    └─► Returns: Final analysis report + all file paths
```

**Key Implementation Details** (power_spectrum_agent.py):

```python
# Line 83-126: Orchestrator creation
orchestrator = CodeAgent(
    name="orchestrator_agent",
    managed_agents=[data_agent, modeling_agent, viz_agent],
    instructions="""
    CRITICAL WORKFLOW:
    1. Data Agent: Load observational data, get file paths
    2. Modeling Agent: Compute theory P(k), pass file paths
    3. Viz Agent: Create plots using both obs and theory file paths

    MUST extract and pass file paths between agents.
    """
)
```

**File-Based Communication**: Agents communicate via file paths, not raw arrays (prevents context overflow)

#### `arxiv_agent`

**Architecture**: Single agent with specialized tools

```
arxiv_agent(query, api_key, llm_url, model_id)
    │
    └─► CodeAgent
        Tools:
        • search_arxiv(query, max_results, sort_by)
        • download_arxiv_paper(paper_id, output_dir)
        • download_full_arxiv_paper(paper_id, output_dir)
        • read_text_file(filepath)
        • list_files(directory)

        Workflow (encoded in system prompt):
        1. Search arXiv for relevant papers
        2. Identify 2-3 most relevant from abstracts
        3. Download PDFs and extract to TXT
        4. Read TXT files to extract information
        5. Return summaries + file paths + citations
```

**Why Agent Tools?**

1. **Complex Orchestration**: Multi-step workflows with conditional logic
2. **Context Management**: Agents handle intermediate results, only return final outputs
3. **Error Recovery**: Agents can retry, adapt strategies if tools fail
4. **Natural Language Interface**: Takes freeform queries, not structured parameters

### 4. Core Implementations (`codes/`)

**Purpose**: Domain logic separate from tool interfaces

**Modules**:
- `cosmology_models.py`: Parameter dict builders for CLASS
- `analysis.py`: CLASS wrapper for power spectrum computation
- `data.py`: File I/O for observational data
- `viz.py`: Matplotlib plotting functions

**Design Rationale**:
- Reusable outside MCP context
- Testable independently
- Can be used directly by Python scripts

### 5. Utilities (`mcp_utils/`)

**path_utils.py**:
```python
def get_output_path(filename: str) -> str:
    """
    Handles output directory logic:
    - Bare filename → prepend 'out/'
    - Absolute path or with separator → use as-is
    - Creates output directory if needed
    """

def get_input_path(filename: str) -> str:
    """Similar logic for input/ directory"""
```

**Purpose**: Consistent path handling across all tools

## Communication Flow

### Client-Server Interaction

```
┌───────────────────┐                           ┌──────────────────┐
│  MCP Client       │                           │  mcp_server.py   │
└─────────┬─────────┘                           └────────┬─────────┘
          │                                              │
          │  1. Launch subprocess                        │
          ├─────────────────────────────────────────────►│
          │     command: python mcp_server.py            │
          │                                              │
          │  2. MCP handshake (stdio)                    │
          │◄────────────────────────────────────────────►│
          │                                              │
          │  3. list_tools()                             │
          ├─────────────────────────────────────────────►│
          │                                              │
          │  4. [Tool schemas: 23 tools]                 │
          │◄─────────────────────────────────────────────┤
          │                                              │
          │                                              │
User asks: "Compare ΛCDM with massive neutrino models"   │
          │                                              │
          │  5. call_tool("LCDM", {})                    │
          ├─────────────────────────────────────────────►│
          │                                              │ Executes
          │  6. {h: 0.6766, Omega_b: 0.02242, ...}       │ LCDM()
          │◄─────────────────────────────────────────────┤
          │                                              │
          │  7. call_tool("nu_mass", {sum_mnu_eV: 0.1})  │
          ├─────────────────────────────────────────────►│
          │                                              │ Executes
          │  8. {h: 0.6766, N_ncdm: 1, m_ncdm: 0.1,...}  │ nu_mass()
          │◄─────────────────────────────────────────────┤
          │                                              │
          │  9. call_tool("compute_power_spectrum", {...})│
          ├─────────────────────────────────────────────►│
          │                                              │ Runs CLASS
          │  10. [P(k) array]                            │ computation
          │◄─────────────────────────────────────────────┤
          │                                              │
          │  ... (more tool calls)                       │
          │                                              │
          │  N. call_tool("plot_power_spectra", {...})   │
          ├─────────────────────────────────────────────►│
          │                                              │ Creates
          │  N+1. "/path/to/out/plot.png"                │ plot
          │◄─────────────────────────────────────────────┤
          │                                              │
User sees analysis + embedded plot                       │
```

### Agent Tool Internal Flow

When `power_spectrum_agent` is called:

```
MCP Client calls tool
    ↓
mcp_server.py:call_tool("power_spectrum_agent", {...})
    ↓
agent_tools/power_spectrum_agent.py:power_spectrum_agent(...)
    ↓
Creates 4 LLM instances (orchestrator + 3 sub-agents)
    ↓
orchestrator.run(query)
    ↓
orchestrator calls data_agent.run("Load eBOSS data")
    ↓ data_agent uses load_observational_data tool
    ↓ data_agent uses save_array tools
    ↓ data_agent returns: "Saved to /path/k.npy, /path/Pk.npy, ..."
orchestrator extracts file paths
    ↓
orchestrator calls modeling_agent.run("Compute ΛCDM and nu_mass P(k)")
    ↓ modeling_agent uses LCDM, nu_mass, create_theory_k_grid tools
    ↓ modeling_agent uses compute_all_models tool
    ↓ modeling_agent uses save_array, save_dict tools
    ↓ modeling_agent returns: "Saved to /path/k_theory.npy, /path/models.npy, ..."
orchestrator extracts file paths
    ↓
orchestrator calls viz_agent.run("Plot comparison with obs and theory from [paths]")
    ↓ viz_agent uses load_array, load_dict tools
    ↓ viz_agent uses plot_power_spectra tool
    ↓ viz_agent returns: "Plot saved to /path/plot.png"
orchestrator assembles final report
    ↓
power_spectrum_agent returns report string
    ↓
mcp_server.py wraps in TextContent
    ↓
MCP Client receives result
```

**Critical Design Choice**: File paths instead of passing arrays
- Avoids context overflow (arrays can be large)
- Persistent intermediate results (debugging, inspection)
- Clear data lineage

## Integration with Claude Desktop

### Setup Process

**1. Install MCP-KE**

```bash
cd /path/to/hep-ke/mcp
pip install -e .
```

This installs:
- Package `mcp-ke` with all dependencies
- Command `mcp-ke` (entry point to mcp_server:main)

**2. Configure Claude Desktop**

Create or edit: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "mcp-ke": {
      "command": "python",
      "args": [
        "/absolute/path/to/hep-ke/mcp/mcp_server.py"
      ],
      "env": {
        "GOOGLE_API_KEY": "your-key-here"
      }
    }
  }
}
```

**Note**: `env` section is optional but required if you want to use agent tools (power_spectrum_agent, arxiv_agent)

**3. Restart Claude Desktop**

Claude Desktop will:
1. Read config on startup
2. Launch `python mcp_server.py` as subprocess
3. Attach stdin/stdout pipes
4. Call `list_tools()` to discover available tools
5. Make tools available in conversation

**4. Verify Connection**

In Claude Desktop, ask: "Can you list the available tools from mcp-ke?"

You should see all 23 tools listed.

### Usage Patterns

**Pattern 1: Direct Tool Usage**

User: "Load the eBOSS data from input/DR14_pm3d_19kbins.txt"

Claude calls: `load_observational_data("DR14_pm3d_19kbins.txt")`

**Pattern 2: Multi-Tool Workflow**

User: "Compare ΛCDM with massive neutrino model (0.1 eV) using eBOSS data"

Claude orchestrates:
1. `load_observational_data(...)`
2. `create_theory_k_grid()`
3. `LCDM()`
4. `nu_mass(0.1)`
5. `compute_power_spectrum(...)` for each model
6. `plot_power_spectra(...)`

**Pattern 3: Agent Tool Usage**

User: "Using the observational data from eBOSS, compare ΛCDM, massive neutrinos, and wCDM models"

Claude calls: `power_spectrum_agent(query="Compare ΛCDM, nu_mass, wCDM models with eBOSS data", api_key=os.getenv("GOOGLE_API_KEY"), ...)`

The agent tool handles the entire workflow internally and returns final analysis.

### Directory Structure Requirements

MCP-KE expects this working directory layout:

```
/your/working/directory/
├── input/              # Input data files (required)
│   └── DR14_pm3d_19kbins.txt
└── out/                # Output files (created automatically)
    ├── *.npy           # Saved arrays
    ├── *.json          # Saved dicts
    └── *.png           # Plot files
```

Tools automatically create `out/` if missing. You must provide `input/` with data files.

## Extension Points

### Adding a New Domain Tool

**Example**: Add a tool for computing distance modulus

```python
# In tools/distance_tools.py

from smolagents import tool

@tool
def compute_distance_modulus(z: float, model_params: dict) -> float:
    """
    Compute distance modulus at redshift z for given cosmology.

    Args:
        z: Redshift
        model_params: Cosmology parameter dict (from LCDM, wCDM, etc.)

    Returns:
        Distance modulus in magnitudes
    """
    from codes.distances import compute_distance_modulus as compute_dm
    return compute_dm(z, model_params)
```

**That's it!** Server auto-discovers on next startup.

**Add to `tools/__init__.py`** (optional, for documentation):

```python
from .distance_tools import compute_distance_modulus

__all__ = [
    ...,
    "compute_distance_modulus",
]
```

### Adding a New Agent Tool

**Example**: Create a model fitting agent

```python
# In agent_tools/fitting_agent.py

from smolagents import CodeAgent, tool
from .llm_helper import create_openai_compatible_llm

@tool
def model_fitting_agent(
    query: str,
    api_key: str,
    llm_url: str,
    model_id: str
) -> str:
    """
    Fit cosmological models to observational data using MCMC.

    Args:
        query: Fitting task description
        api_key: API key for LLM
        llm_url: LLM API endpoint
        model_id: Model identifier

    Returns:
        Fitting results and parameter constraints
    """
    model = create_openai_compatible_llm(api_key, llm_url, model_id)

    # Import relevant tools for this agent
    from tools import (
        load_observational_data,
        LCDM,
        compute_power_spectrum,
    )

    # Create custom MCMC tools
    @tool
    def run_mcmc_chain(params, data, n_steps):
        # Implementation here
        pass

    agent = CodeAgent(
        model=model,
        tools=[
            load_observational_data,
            LCDM,
            compute_power_spectrum,
            run_mcmc_chain,
        ],
        max_steps=50,
        name="fitting_agent",
        instructions="Your fitting workflow instructions here..."
    )

    return str(agent.run(query))
```

**Auto-discovered!** No registration needed.

### Modifying Tool Discovery

To customize which tools are exposed, edit `mcp_server.py:discover_tools()`:

```python
# Example: Filter out agent tools
discovered_tools = {}
for package in [tools]:  # Remove agent_tools from list
    # ... discovery logic
```

Or filter by name:

```python
# Example: Only expose tools starting with "plot_"
if not tool_name.startswith("plot_"):
    continue
```

## Design Rationale

### Why MCP?

**Pros**:
- Standard protocol for LLM-tool communication
- Supported by major AI platforms (Anthropic, etc.)
- Language-agnostic (JSON-RPC over stdio)
- Secure subprocess isolation
- Simple deployment (no servers, ports, or networking)

**Cons**:
- Still evolving standard
- Limited to stdio communication (no streaming large data)
- Requires client support

**Alternative Considered**: REST API
- Would require managing server lifecycle, ports, authentication
- More complex deployment
- MCP is simpler for local development and Claude Desktop integration

### Why Smolagents?

**smolagents** is Hugging Face's lightweight agent framework:
- Simple `@tool` decorator
- Built-in `CodeAgent` for multi-step reasoning
- Support for managed sub-agents (hierarchical orchestration)
- LLM-agnostic (works with any OpenAI-compatible API)

**Alternative Considered**: LangChain
- More features but heavier dependencies
- smolagents is more focused and easier to understand
- Better fit for tool-centric design

### Why Two-Tier Tool System?

**Domain Tools**:
- Composable primitives
- Testable in isolation
- Reusable across workflows
- Low latency

**Agent Tools**:
- Handle complex, multi-step workflows
- Reduce client orchestration burden
- Encapsulate domain expertise
- Higher latency but much more capable

**Benefit**: Clients can choose appropriate abstraction level

### Why File-Based Agent Communication?

**Problem**: Passing large NumPy arrays between agents overflows context

**Solution**: Agents pass file paths, not data
- File: `/path/to/out/k_theory.npy`
- Next agent loads with `load_array`

**Pros**:
- Bounded context usage
- Persistent intermediate results (debugging, inspection)
- Clear data lineage

**Cons**:
- Requires shared filesystem
- Manual cleanup needed

**Alternative Considered**: Structured message passing
- Would require serialization/deserialization
- Still faces size limits
- File system is simpler

## Testing Strategy

### Unit Tests

**Domain tools**: `tests/test_domain_tools.py`
```python
def test_LCDM():
    params = LCDM()
    assert params['h'] == 0.6766
    assert 'Omega_b' in params
```

**No API key required** - tests use mocked responses

### Integration Tests

**Agent tools**: `tests/test_agent_tools.py`
```python
@pytest.mark.skipif(not os.getenv("GOOGLE_API_KEY"), reason="API key required")
def test_power_spectrum_agent():
    result = power_spectrum_agent(
        query="Compare ΛCDM with eBOSS data",
        api_key=os.getenv("GOOGLE_API_KEY"),
        llm_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        model_id="gemini-2.0-flash-exp"
    )
    assert "plot" in result.lower()
```

**Requires API key** - tests make real LLM calls

### Running Tests

```bash
# Unit tests only (fast, no API key)
pytest tests/test_domain_tools.py

# All tests (requires GOOGLE_API_KEY)
export GOOGLE_API_KEY="your-key"
pytest tests/ -v
```

## Performance Considerations

### Domain Tools
- **Latency**: ~10-100ms per tool call (depends on CLASS computation)
- **Bottleneck**: CLASS computations (CPU-bound)
- **Scaling**: Stateless, can parallelize across calls

### Agent Tools
- **Latency**: ~30-120 seconds per workflow
- **Bottleneck**: LLM API calls (network + inference)
- **Scaling**: Limited by LLM API rate limits

### MCP Server
- **Startup**: ~1-2 seconds (tool discovery + imports)
- **Memory**: ~200MB base + CLASS memory (~50-100MB per computation)
- **Concurrent calls**: Not parallelized (stdio is serial)

## Security Considerations

### Code Execution

**Agent tools use `CodeAgent`** which can execute arbitrary Python code:
- Only executes code generated by LLM
- Constrained to `additional_authorized_imports`
- Runs in same process (no sandboxing)

**Mitigation**:
- Use trusted LLMs only
- Review agent instructions carefully
- Monitor output directories for unexpected files

### API Key Handling

Agent tools require API keys:
- Passed as function arguments (not ideal for secrets)
- Visible in MCP traffic (stdio is local-only)
- Better: Read from environment in agent tool implementation

**Recommended pattern**:
```python
@tool
def power_spectrum_agent(query: str) -> str:
    """Don't require api_key as parameter"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "Error: GOOGLE_API_KEY not set"
    # ... rest of implementation
```

### File System Access

Tools read/write to `input/` and `out/` directories:
- No path traversal protection currently
- Tools can write anywhere if given absolute paths

**Future improvement**: Add path validation in `mcp_utils.path_utils`

## Future Enhancements

### 1. Streaming Results
- MCP supports streaming but not used currently
- Would benefit long-running agent tools
- Show progress as agents work

### 2. Tool Caching
- Cache CLASS computations (expensive)
- Key by parameter hash
- Significant speedup for repeated queries

### 3. More Agent Tools
- `mcmc_fitting_agent`: Bayesian parameter fitting
- `literature_review_agent`: Systematic paper analysis
- `data_pipeline_agent`: End-to-end analysis workflows

### 4. Better Error Handling
- Structured error responses (not just strings)
- Retry logic for transient failures
- Detailed diagnostic information

### 5. Observability
- Logging framework for debugging
- Metrics collection (tool usage, latency)
- Agent trace visualization

## Conclusion

MCP-KE demonstrates a practical pattern for exposing domain expertise through AI-accessible tools. By combining simple atomic tools with complex agent-based workflows, it provides flexibility for both basic automation and sophisticated analysis tasks.

The **tools-as-agents** pattern allows clients to choose the appropriate level of abstraction: call individual tools for fine-grained control, or use agent tools for end-to-end workflows. This design scales from simple data queries to complex multi-step analyses while maintaining a uniform interface through the MCP protocol.

## References

- **MCP Specification**: https://modelcontextprotocol.io/
- **Smolagents**: https://github.com/huggingface/smolagents
- **CLASS**: https://github.com/lesgourg/class_public
- **eBOSS DR14**: https://data.sdss.org/sas/dr14/eboss/lss/
