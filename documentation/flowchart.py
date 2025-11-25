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
        c.node('claude', 'Claude Desktop\nor Custom Agent', shape='box', style='filled', fillcolor='lightblue')

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
    Detailed view of power_spectrum_agent's internal 4-agent orchestration,
    showing file-based communication and tool usage.
    """
    dot = Digraph('Power_Spectrum_Agent')
    dot.attr(rankdir='TB', fontsize='9', labelloc='t',
             label='power_spectrum_agent: Multi-Agent Workflow with File-Based Communication')

    # MCP Client view
    with dot.subgraph(name='cluster_outer') as c:
        c.attr(label='MCP Client (Claude Desktop)', style='rounded', color='blue')
        c.node('claude', 'Claude Desktop', shape='box', style='filled', fillcolor='lightblue')
        c.node('toolcall', 'call_tool:\npower_spectrum_agent(\n  query="Compare ΛCDM...",\n  api_key="...",\n  llm_url="...",\n  model_id="..."\n)',
               shape='box', style='filled', fillcolor='lightblue', fontsize='8')

    # Orchestrator
    dot.node('orch_agent', 'Orchestrator Agent\n\nCoordinates workflow\nPasses file paths between agents',
             shape='box', style='filled', fillcolor='wheat')

    # Data Agent
    with dot.subgraph(name='cluster_data') as data_c:
        data_c.attr(label='Data Agent', style='rounded', color='green', fontsize='8')
        data_c.node('data_agent', 'data_agent', shape='box', style='filled', fillcolor='lightgreen', fontsize='8')
        data_c.node('data_tools', 'Tools:\n• load_observational_data\n• save_array, save_dict',
                    shape='box', style='dashed', fillcolor='lightgreen', fontsize='7')
        data_c.node('data_output', 'Saves:\nk_obs.npy\nPk_obs.npy\nerrors_obs.npy',
                    shape='note', fillcolor='lightyellow', fontsize='7')

    # Modeling Agent
    with dot.subgraph(name='cluster_model') as model_c:
        model_c.attr(label='Modeling Agent', style='rounded', color='cyan', fontsize='8')
        model_c.node('model_agent', 'modeling_agent', shape='box', style='filled', fillcolor='lightcyan', fontsize='8')
        model_c.node('model_tools', 'Tools:\n• LCDM, nu_mass, wCDM\n• create_theory_k_grid\n• compute_all_models\n• load/save_array',
                     shape='box', style='dashed', fillcolor='lightcyan', fontsize='7')
        model_c.node('model_output', 'Saves:\nk_theory.npy\nmodel_results.npy',
                     shape='note', fillcolor='lightyellow', fontsize='7')

    # Viz Agent
    with dot.subgraph(name='cluster_viz') as viz_c:
        viz_c.attr(label='Viz Agent', style='rounded', color='pink', fontsize='8')
        viz_c.node('viz_agent', 'viz_agent', shape='box', style='filled', fillcolor='lightpink', fontsize='8')
        viz_c.node('viz_tools', 'Tools:\n• plot_power_spectra\n• load_array, load_dict',
                   shape='box', style='dashed', fillcolor='lightpink', fontsize='7')
        viz_c.node('viz_output', 'Saves:\nplot.png',
                   shape='note', fillcolor='lightyellow', fontsize='7')

    # Final output
    dot.node('final_report', 'Final Report:\n\n• Analysis summary\n• All file paths',
             shape='box', style='filled', fillcolor='gold', fontsize='8')

    # Flow edges
    dot.edge('claude', 'toolcall', label='User query', fontsize='7')
    dot.edge('toolcall', 'orch_agent', label='1. Forwarded', fontsize='7', color='purple')

    # Data agent flow
    dot.edge('orch_agent', 'data_agent', label='2. "Load eBOSS"', fontsize='7', color='green')
    dot.edge('data_agent', 'data_tools', style='dashed', fontsize='7')
    dot.edge('data_tools', 'data_output', fontsize='7')
    dot.edge('data_agent', 'orch_agent', label='3. File paths:\n/out/k_obs.npy\n...',
             fontsize='7', color='green')

    # Modeling agent flow
    dot.edge('orch_agent', 'model_agent', label='4. "Compute models"', fontsize='7', color='cyan')
    dot.edge('model_agent', 'model_tools', style='dashed', fontsize='7')
    dot.edge('model_tools', 'model_output', fontsize='7')
    dot.edge('model_agent', 'orch_agent', label='5. File paths:\n/out/k_theory.npy\n...',
             fontsize='7', color='cyan')

    # Viz agent flow
    dot.edge('orch_agent', 'viz_agent', label='6. "Plot" + paths', fontsize='7', color='pink')
    dot.edge('viz_agent', 'viz_tools', style='dashed', fontsize='7')
    dot.edge('viz_tools', 'viz_output', fontsize='7')
    dot.edge('viz_agent', 'orch_agent', label='7. File paths:\n/out/plot.png',
             fontsize='7', color='pink')

    # Final assembly
    dot.edge('orch_agent', 'final_report', label='8. Assemble', fontsize='7', color='orange')
    dot.edge('final_report', 'claude', label='9. Return', fontsize='7', color='purple', penwidth='2')

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