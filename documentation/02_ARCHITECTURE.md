# MCP-KE Architecture

## High-Level Design

MCP-KE follows a tool server pattern where domain-specific cosmology analysis capabilities are exposed through the Model Context Protocol (MCP). The system has three main architectural layers:

### Architecture Overview

See the generated diagrams for visual representations:
- **abstract_architecture.png**: High-level abstract architecture showing the tool server pattern
- **mcp_ke_overview.png**: Detailed architecture with all components and tools
- **power_spectrum_agent.png**: Internal workflow of the power_spectrum_agent

The architecture can be summarized as:

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

See **power_spectrum_agent.png** for a detailed visual workflow.

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

## Directory Structure Requirements

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
