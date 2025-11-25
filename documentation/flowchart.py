from graphviz import Digraph

def abstract_architecture():
    """
    High-level abstract architecture - generic and extensible view.
    Shows MCP-KE as a tool server pattern without specific implementation details.
    """
    dot = Digraph('Abstract_Architecture')
    dot.attr(rankdir='LR', fontsize='11', labelloc='t',
             label='MCP-KE: Tool Server Pattern')

    # MCP Client Layer
    with dot.subgraph(name='cluster_client') as c:
        c.attr(label='MCP Client Layer', style='rounded', color='blue')
        c.node('client', 'MCP Client\n\n(Any AI system or\napplication)', shape='box', style='filled', fillcolor='lightblue')

    # MCP Server Core
    with dot.subgraph(name='cluster_server') as s:
        s.attr(label='MCP-KE Server', style='rounded', color='green')
        s.node('server', 'MCP Server\n\nAuto-discovery\nTool execution\nstdio communication',
               shape='box', style='filled', fillcolor='lightgreen')

        # Domain Tools
        with s.subgraph(name='cluster_domain') as d:
            d.attr(label='Domain Tools', style='rounded', fontsize='10', color='orange')
            d.node('data_cat', 'Data Loading', shape='box', fontsize='9', style='filled', fillcolor='lightyellow')
            d.node('model_cat', 'Model Parameters', shape='box', fontsize='9', style='filled', fillcolor='lightyellow')
            d.node('analysis_cat', 'Analysis & Computation', shape='box', fontsize='9', style='filled', fillcolor='lightyellow')
            d.node('viz_cat', 'Visualization', shape='box', fontsize='9', style='filled', fillcolor='lightyellow')
            d.node('util_cat', 'Utilities', shape='box', fontsize='9', style='filled', fillcolor='lightyellow')

        # Agent Tools
        with s.subgraph(name='cluster_agent') as a:
            a.attr(label='Agent Tools', style='rounded', fontsize='10', color='purple')
            a.node('agent1', 'power_spectrum_agent', shape='box', fontsize='9', style='filled', fillcolor='plum')
            a.node('agent2', 'arxiv_agent', shape='box', fontsize='9', style='filled', fillcolor='plum')
            a.node('agent_more', '...other agents', shape='box', fontsize='9', style='dashed', fillcolor='plum')

    # Core Implementation Layer
    with dot.subgraph(name='cluster_core') as core:
        core.attr(label='Core Domain Logic', style='dashed', fontsize='10', color='gray')
        core.node('codes', 'Domain implementations\n(cosmology, analysis, viz...)',
                  shape='box', fontsize='9', style='filled', fillcolor='lightgray')

    # External Services
    with dot.subgraph(name='cluster_external') as e:
        e.attr(label='External Services', style='dashed', fontsize='10', color='red')
        e.node('llm_apis', 'LLM APIs', shape='ellipse', fontsize='9', style='filled', fillcolor='mistyrose')
        e.node('data_apis', 'Data APIs\n(arXiv, etc.)', shape='ellipse', fontsize='9', style='filled', fillcolor='mistyrose')
        e.node('compute', 'Compute Libraries', shape='ellipse', fontsize='9', style='filled', fillcolor='mistyrose')

    # Main connections
    dot.edge('client', 'server', label='MCP\nProtocol', fontsize='9', color='blue', penwidth='3')

    # Server to tools
    dot.edge('server', 'data_cat', style='solid', color='green')
    dot.edge('server', 'model_cat', style='solid', color='green')
    dot.edge('server', 'analysis_cat', style='solid', color='green')
    dot.edge('server', 'viz_cat', style='solid', color='green')
    dot.edge('server', 'util_cat', style='solid', color='green')
    dot.edge('server', 'agent1', style='solid', color='purple')
    dot.edge('server', 'agent2', style='solid', color='purple')
    dot.edge('server', 'agent_more', style='dashed', color='purple')

    # Tools use core implementations
    dot.edge('data_cat', 'codes', style='dashed', label='use', fontsize='8', color='gray')
    dot.edge('model_cat', 'codes', style='dashed', fontsize='8', color='gray')
    dot.edge('analysis_cat', 'codes', style='dashed', fontsize='8', color='gray')
    dot.edge('viz_cat', 'codes', style='dashed', fontsize='8', color='gray')

    # External dependencies
    dot.edge('agent1', 'llm_apis', style='dashed', label='require', fontsize='8', color='red')
    dot.edge('agent2', 'llm_apis', style='dashed', fontsize='8', color='red')
    dot.edge('agent2', 'data_apis', style='dashed', fontsize='8', color='red')
    dot.edge('analysis_cat', 'compute', style='dashed', label='use', fontsize='8', color='red')

    return dot


def mcp_overview():
    """
    High-level architecture showing MCP client-server relationship,
    domain tools vs agent tools, and external dependencies.
    """
    dot = Digraph('MCP_KE_Overview')
    dot.attr(rankdir='LR', fontsize='10', labelloc='t',
             label='MCP-KE Architecture: Tool Server with Domain & Agent Tools')

    # MCP Client Layer
    with dot.subgraph(name='cluster_client') as c:
        c.attr(label='MCP Client Layer', style='rounded', color='blue')
        c.node('claude', 'Custom Agent \nor Claude Desktop', shape='box', style='filled', fillcolor='lightblue')

    # MCP Server Core
    with dot.subgraph(name='cluster_server') as s:
        s.attr(label='mcp-ke MCP Server', style='rounded', color='green')
        s.node('server', 'mcp_server.py\n\n• Auto-discover @tool functions\n• Build MCP Tool schemas\n• Handle tool execution\n• stdio communication',
               shape='box', style='filled', fillcolor='lightgreen')

        # Domain Tools
        with s.subgraph(name='cluster_domain') as d:
            d.attr(label='Domain Tools (tools/) - 16 tools', style='rounded', fontsize='9', color='orange')
            d.node('t1', 'Model Parameters\nLCDM(), nu_mass()\nwCDM()',
                   shape='box', fontsize='8', style='filled', fillcolor='lightyellow')
            d.node('t2', 'Power Spectrum\ncompute_power_spectrum()\ncompute_all_models()\ncompute_suppression_ratios()',
                   shape='box', fontsize='8', style='filled', fillcolor='lightyellow')
            d.node('t3', 'Data Loading\nload_observational_data()\ncreate_theory_k_grid()',
                   shape='box', fontsize='8', style='filled', fillcolor='lightyellow')
            d.node('t4', 'Visualization\nplot_power_spectra()\nplot_suppression_ratios()',
                   shape='box', fontsize='8', style='filled', fillcolor='lightyellow')
            d.node('t5', 'Utilities\nsave/load_array()\nsave/load_dict()\nlist_agent_files()',
                   shape='box', fontsize='8', style='filled', fillcolor='lightyellow')

        # Agent Tools
        with s.subgraph(name='cluster_agent') as a:
            a.attr(label='Agent Tools (agent_tools/) - 2 tools', style='rounded', fontsize='9', color='purple')
            a.node('a1', 'power_spectrum_agent\n\n4-agent orchestration:\n• orchestrator\n• data_agent\n• modeling_agent\n• viz_agent',
                   shape='box', fontsize='8', style='filled', fillcolor='plum')
            a.node('a2', 'arxiv_agent\n\nSingle agent with tools:\n• search_arxiv\n• download_full_arxiv_paper\n• read_text_file',
                   shape='box', fontsize='8', style='filled', fillcolor='plum')

    # Core Implementation Layer
    with dot.subgraph(name='cluster_core') as core:
        core.attr(label='Core Implementation (codes/)', style='dashed', fontsize='9', color='gray')
        core.node('codes', 'cosmology_models.py\nanalysis.py\ndata.py\nviz.py',
                  shape='box', fontsize='8', style='filled', fillcolor='lightgray')

    # External Services
    with dot.subgraph(name='cluster_external') as e:
        e.attr(label='External Services', style='dashed', fontsize='9', color='red')
        e.node('class', 'CLASS\nCosmology code', shape='ellipse', fontsize='8', style='filled', fillcolor='mistyrose')
        e.node('eboss', 'eBOSS DR14\nObservational data', shape='ellipse', fontsize='8', style='filled', fillcolor='mistyrose')
        e.node('arxiv', 'arXiv API\nPaper database', shape='ellipse', fontsize='8', style='filled', fillcolor='mistyrose')
        e.node('llm', 'LLM APIs\n(Anthropic, Google, etc.)', shape='ellipse', fontsize='8', style='filled', fillcolor='mistyrose')

    # Main connections
    dot.edge('claude', 'server', label='MCP Protocol\n(stdio)', fontsize='8', color='blue', penwidth='2')
    dot.edge('server', 't1', style='solid', color='green')
    dot.edge('server', 't2', style='solid', color='green')
    dot.edge('server', 't3', style='solid', color='green')
    dot.edge('server', 't4', style='solid', color='green')
    dot.edge('server', 't5', style='solid', color='green')
    dot.edge('server', 'a1', style='solid', color='purple')
    dot.edge('server', 'a2', style='solid', color='purple')

    # Tools use codes/
    dot.edge('t1', 'codes', style='dashed', label='uses', fontsize='7', color='gray')
    dot.edge('t2', 'codes', style='dashed', label='uses', fontsize='7', color='gray')
    dot.edge('t3', 'codes', style='dashed', label='uses', fontsize='7', color='gray')
    dot.edge('t4', 'codes', style='dashed', label='uses', fontsize='7', color='gray')

    # External dependencies
    dot.edge('t2', 'class', style='dashed', label='calls', fontsize='7', color='red')
    dot.edge('t3', 'eboss', style='dashed', label='reads', fontsize='7', color='red')
    dot.edge('a2', 'arxiv', style='dashed', label='queries', fontsize='7', color='red')
    dot.edge('a1', 'class', style='dashed', label='calls', fontsize='7', color='red')
    dot.edge('a1', 'llm', style='dashed', label='requires', fontsize='7', color='red')
    dot.edge('a2', 'llm', style='dashed', label='requires', fontsize='7', color='red')

    return dot

def power_spectrum_agent_internals():
    """
    Simplified generic view of multi-agent orchestration showing dataflow.
    """
    dot = Digraph('Power_Spectrum_Agent')
    dot.attr(rankdir='TB', fontsize='10', labelloc='t',
             label='Multi-Agent Orchestration: Generic Dataflow Pattern')

    # MCP Client
    dot.node('client', 'MCP Client', shape='box', style='filled', fillcolor='lightblue', fontsize='10')

    # Agent tool entry point
    dot.node('agent_tool', 'Agent Tool\n(e.g., power_spectrum_agent)',
             shape='box', style='filled,rounded', fillcolor='lavender', fontsize='10')

    # Orchestrator
    dot.node('orchestrator', 'Orchestrator Agent\n\nCoordinates sub-agents\nManages dataflow',
             shape='box', style='filled', fillcolor='wheat', fontsize='10')

    # Sub-agents in a row
    dot.node('agent1', 'Sub-Agent 1\n\nData Loading',
             shape='box', style='filled', fillcolor='lightgreen', fontsize='9')
    dot.node('agent2', 'Sub-Agent 2\n\nProcessing',
             shape='box', style='filled', fillcolor='lightcyan', fontsize='9')
    dot.node('agent3', 'Sub-Agent 3\n\nVisualization',
             shape='box', style='filled', fillcolor='lightpink', fontsize='9')

    # Results
    dot.node('results', 'Results', shape='box', style='filled', fillcolor='gold', fontsize='10')

    # Main flow
    dot.edge('client', 'agent_tool', label='1. Query', fontsize='9', penwidth='2', color='blue')
    dot.edge('agent_tool', 'orchestrator', label='2. Initialize', fontsize='9', color='purple')

    # Orchestrator to sub-agents
    dot.edge('orchestrator', 'agent1', label='3. Task 1', fontsize='8', color='green')
    dot.edge('agent1', 'orchestrator', label='Data', fontsize='8', color='green', style='dashed')

    dot.edge('orchestrator', 'agent2', label='4. Task 2', fontsize='8', color='cyan')
    dot.edge('agent2', 'orchestrator', label='Results', fontsize='8', color='cyan', style='dashed')

    dot.edge('orchestrator', 'agent3', label='5. Task 3', fontsize='8', color='pink')
    dot.edge('agent3', 'orchestrator', label='Outputs', fontsize='8', color='pink', style='dashed')

    # Final results
    dot.edge('orchestrator', 'results', label='6. Assemble', fontsize='9', color='orange')
    dot.edge('results', 'client', label='7. Return', fontsize='9', penwidth='2', color='blue')

    return dot


if __name__ == '__main__':
    print("Generating flowcharts...")

    d0 = abstract_architecture()
    d0.render('abstract_architecture', format='png', cleanup=True)
    print("✓ Generated abstract_architecture.png")

    d1 = mcp_overview()
    d1.render('mcp_ke_overview', format='png', cleanup=True)
    print("✓ Generated mcp_ke_overview.png")

    d2 = power_spectrum_agent_internals()
    d2.render('power_spectrum_agent', format='png', cleanup=True)
    print("✓ Generated power_spectrum_agent.png")

    print("\nAll flowcharts generated successfully!")