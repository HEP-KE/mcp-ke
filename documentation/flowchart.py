from graphviz import Digraph

def abstract_architecture():
    """
    High-level abstract architecture - generic and extensible view.
    Shows MCP-KE as a tool server pattern without specific implementation details.
    """
    dot = Digraph('Abstract_Architecture')
    dot.attr(rankdir='LR', 
             fontsize='18',
             fontname='Helvetica-Bold',
             labelloc='t',
             label='MCP-KE: Tool Server Pattern',
             bgcolor='#FAFAFA',
             pad='0.2',
             nodesep='0.3',
             ranksep='0.5',
             dpi='300')
    
    # Set default node attributes
    dot.node_attr.update(fontname='Helvetica', fontsize='13')
    dot.edge_attr.update(fontname='Helvetica', fontsize='11')

    # MCP Client Layer
    with dot.subgraph(name='cluster_client') as c:
        c.attr(label='MCP Client Layer',
               style='rounded,filled',
               fillcolor='#E8F4FD',
               color='#1976D2',
               penwidth='2',
               fontsize='14',
               fontname='Helvetica-Bold')
        c.node('client', 'MCP Client\n\n(Any AI system or\napplication)',
               shape='box',
               style='rounded,filled',
               fillcolor='#2196F3',
               fontcolor='white',
               fontsize='13',
               penwidth='0')

    # MCP Server Core
    with dot.subgraph(name='cluster_server') as s:
        s.attr(label='MCP-KE Server',
               style='rounded,filled',
               fillcolor='#F1F8E9',
               color='#689F38',
               penwidth='2',
               fontsize='14',
               fontname='Helvetica-Bold')
        s.node('server', 'MCP Server\n\nAuto-discovery\nTool execution\nstdio communication',
               shape='box',
               style='rounded,filled',
               fillcolor='#8BC34A',
               fontcolor='white',
               fontsize='13',
               penwidth='0')

        # Domain Tools
        with s.subgraph(name='cluster_domain') as d:
            d.attr(label='Domain Tools',
                   style='rounded,filled',
                   fillcolor='#FFF3E0',
                   color='#F57C00',
                   penwidth='1.5',
                   fontsize='13',
                   fontname='Helvetica-Bold')
            d.node('data_cat', 'Data Loading',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#FFB74D',
                   fontcolor='#424242',
                   fontsize='12',
                   penwidth='0')
            d.node('model_cat', 'Model Parameters',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#FFB74D',
                   fontcolor='#424242',
                   fontsize='12',
                   penwidth='0')
            d.node('analysis_cat', 'Analysis & Computation',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#FFB74D',
                   fontcolor='#424242',
                   fontsize='12',
                   penwidth='0')
            d.node('viz_cat', 'Visualization',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#FFB74D',
                   fontcolor='#424242',
                   fontsize='12',
                   penwidth='0')
            d.node('util_cat', 'Utilities',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#FFB74D',
                   fontcolor='#424242',
                   fontsize='12',
                   penwidth='0')

        # Agent Tools
        with s.subgraph(name='cluster_agent') as a:
            a.attr(label='Agent Tools',
                   style='rounded,filled',
                   fillcolor='#F3E5F5',
                   color='#7B1FA2',
                   penwidth='1.5',
                   fontsize='13',
                   fontname='Helvetica-Bold')
            a.node('agent1', 'power_spectrum_agent',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#BA68C8',
                   fontcolor='white',
                   fontsize='12',
                   penwidth='0')
            a.node('agent2', 'arxiv_agent',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#BA68C8',
                   fontcolor='white',
                   fontsize='12',
                   penwidth='0')
            a.node('agent_more', '...other agents',
                   shape='box',
                   style='rounded,dashed,filled',
                   fillcolor='#E1BEE7',
                   fontcolor='#4A148C',
                   fontsize='12',
                   penwidth='1.5',
                   color='#7B1FA2')

    # Core Implementation Layer
    with dot.subgraph(name='cluster_core') as core:
        core.attr(label='Core Domain Logic',
                  style='dashed,rounded',
                  color='#616161',
                  penwidth='1.5',
                  fontsize='13',
                  fontname='Helvetica')
        core.node('codes', 'Domain implementations\n(cosmology, analysis, viz...)',
                  shape='box',
                  style='rounded,filled',
                  fillcolor='#ECEFF1',
                  fontcolor='#37474F',
                  fontsize='12',
                  penwidth='0')

    # External Services
    with dot.subgraph(name='cluster_external') as e:
        e.attr(label='External Services',
               style='dashed,rounded',
               color='#D32F2F',
               penwidth='1.5',
               fontsize='13',
               fontname='Helvetica')
        e.node('llm_apis', 'LLM APIs',
               shape='ellipse',
               style='filled',
               fillcolor='#FFCDD2',
               fontcolor='#B71C1C',
               fontsize='12',
               penwidth='0')
        e.node('data_apis', 'Data APIs\n(arXiv, etc.)',
               shape='ellipse',
               style='filled',
               fillcolor='#FFCDD2',
               fontcolor='#B71C1C',
               fontsize='12',
               penwidth='0')
        e.node('compute', 'Compute Libraries',
               shape='ellipse',
               style='filled',
               fillcolor='#FFCDD2',
               fontcolor='#B71C1C',
               fontsize='12',
               penwidth='0')

    # Main connections
    dot.edge('client', 'server',
             label='MCP\nProtocol',
             fontsize='11',
             color='#1565C0',
             penwidth='3',
             arrowhead='vee')

    # Server to tools
    dot.edge('server', 'data_cat', color='#558B2F', penwidth='2', arrowhead='vee')
    dot.edge('server', 'model_cat', color='#558B2F', penwidth='2', arrowhead='vee')
    dot.edge('server', 'analysis_cat', color='#558B2F', penwidth='2', arrowhead='vee')
    dot.edge('server', 'viz_cat', color='#558B2F', penwidth='2', arrowhead='vee')
    dot.edge('server', 'util_cat', color='#558B2F', penwidth='2', arrowhead='vee')
    dot.edge('server', 'agent1', color='#6A1B9A', penwidth='2', arrowhead='vee')
    dot.edge('server', 'agent2', color='#6A1B9A', penwidth='2', arrowhead='vee')
    dot.edge('server', 'agent_more', style='dashed', color='#6A1B9A', penwidth='1.5', arrowhead='vee')

    # Tools use core implementations
    dot.edge('data_cat', 'codes', style='dashed', label='use', fontsize='10', color='#757575', penwidth='1', arrowhead='open')
    dot.edge('model_cat', 'codes', style='dashed', fontsize='10', color='#757575', penwidth='1', arrowhead='open')
    dot.edge('analysis_cat', 'codes', style='dashed', fontsize='10', color='#757575', penwidth='1', arrowhead='open')
    dot.edge('viz_cat', 'codes', style='dashed', fontsize='10', color='#757575', penwidth='1', arrowhead='open')

    # External dependencies
    dot.edge('agent1', 'llm_apis', style='dashed', label='require', fontsize='10', color='#C62828', penwidth='1', arrowhead='open')
    dot.edge('agent2', 'llm_apis', style='dashed', fontsize='10', color='#C62828', penwidth='1', arrowhead='open')
    dot.edge('agent2', 'data_apis', style='dashed', fontsize='10', color='#C62828', penwidth='1', arrowhead='open')
    dot.edge('analysis_cat', 'compute', style='dashed', label='use', fontsize='10', color='#C62828', penwidth='1', arrowhead='open')

    return dot


def mcp_overview():
    """
    High-level architecture showing MCP client-server relationship,
    domain tools vs agent tools, and external dependencies.
    """
    dot = Digraph('MCP_KE_Overview')
    dot.attr(rankdir='LR',
             fontsize='18',
             fontname='Helvetica-Bold',
             labelloc='t',
             label='MCP-KE Architecture: Tool Server with Domain & Agent Tools',
             bgcolor='#FAFAFA',
             pad='0.2',
             nodesep='0.3',
             ranksep='0.5',
             dpi='300')
    
    # Set default node attributes
    dot.node_attr.update(fontname='Helvetica', fontsize='11')
    dot.edge_attr.update(fontname='Helvetica', fontsize='10')

    # MCP Client Layer
    with dot.subgraph(name='cluster_client') as c:
        c.attr(label='MCP Client Layer',
               style='rounded,filled',
               fillcolor='#E3F2FD',
               color='#1565C0',
               penwidth='2',
               fontsize='14',
               fontname='Helvetica-Bold')
        c.node('claude', 'Custom Agent\nor Claude Desktop',
               shape='box',
               style='rounded,filled',
               fillcolor='#1E88E5',
               fontcolor='white',
               fontsize='12',
               penwidth='0')

    # MCP Server Core
    with dot.subgraph(name='cluster_server') as s:
        s.attr(label='mcp-ke MCP Server',
               style='rounded,filled',
               fillcolor='#E8F5E9',
               color='#43A047',
               penwidth='2',
               fontsize='14',
               fontname='Helvetica-Bold')
        s.node('server', 'mcp_server.py\n\n• Auto-discover @tool functions\n• Build MCP Tool schemas\n• Handle tool execution\n• stdio communication',
               shape='box',
               style='rounded,filled',
               fillcolor='#66BB6A',
               fontcolor='white',
               penwidth='0',
               fontsize='11')

        # Domain Tools
        with s.subgraph(name='cluster_domain') as d:
            d.attr(label='Domain Tools (tools/) - 16 tools',
                   style='rounded,filled',
                   fillcolor='#FFF8E1',
                   color='#FFA000',
                   penwidth='1.5',
                   fontsize='12',
                   fontname='Helvetica-Bold')
            d.node('t1', 'Model Parameters\nLCDM(), nu_mass()\nwCDM()',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#FFCA28',
                   fontcolor='#424242',
                   penwidth='0',
                   fontsize='10')
            d.node('t2', 'Power Spectrum\ncompute_power_spectrum()\ncompute_all_models()\ncompute_suppression_ratios()',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#FFCA28',
                   fontcolor='#424242',
                   penwidth='0',
                   fontsize='10')
            d.node('t3', 'Data Loading\nload_observational_data()\ncreate_theory_k_grid()',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#FFCA28',
                   fontcolor='#424242',
                   penwidth='0',
                   fontsize='10')
            d.node('t4', 'Visualization\nplot_power_spectra()\nplot_suppression_ratios()',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#FFCA28',
                   fontcolor='#424242',
                   penwidth='0',
                   fontsize='10')
            d.node('t5', 'Utilities\nsave/load_array()\nsave/load_dict()\nlist_agent_files()',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#FFCA28',
                   fontcolor='#424242',
                   penwidth='0',
                   fontsize='10')

        # Agent Tools
        with s.subgraph(name='cluster_agent') as a:
            a.attr(label='Agent Tools (agent_tools/) - 2 tools',
                   style='rounded,filled',
                   fillcolor='#EDE7F6',
                   color='#5E35B1',
                   penwidth='1.5',
                   fontsize='12',
                   fontname='Helvetica-Bold')
            a.node('a1', 'power_spectrum_agent\n\n4-agent orchestration:\n• orchestrator\n• data_agent\n• modeling_agent\n• viz_agent',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#9575CD',
                   fontcolor='white',
                   penwidth='0',
                   fontsize='10')
            a.node('a2', 'arxiv_agent\n\nSingle agent with tools:\n• search_arxiv\n• download_full_arxiv_paper\n• read_text_file',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#9575CD',
                   fontcolor='white',
                   penwidth='0',
                   fontsize='10')

    # Core Implementation Layer
    with dot.subgraph(name='cluster_core') as core:
        core.attr(label='Core Implementation (codes/)',
                  style='dashed,rounded',
                  color='#546E7A',
                  penwidth='1.5',
                  fontsize='12',
                  fontname='Helvetica')
        core.node('codes', 'cosmology_models.py\nanalysis.py\ndata.py\nviz.py',
                  shape='box',
                  style='rounded,filled',
                  fillcolor='#CFD8DC',
                  fontcolor='#263238',
                  penwidth='0',
                  fontsize='10')

    # External Services
    with dot.subgraph(name='cluster_external') as e:
        e.attr(label='External Services',
               style='dashed,rounded',
               color='#E53935',
               penwidth='1.5',
               fontsize='12',
               fontname='Helvetica')
        e.node('class', 'CLASS\nCosmology code',
               shape='ellipse',
               style='filled',
               fillcolor='#FFEBEE',
               fontcolor='#C62828',
               penwidth='0',
               fontsize='10')
        e.node('eboss', 'eBOSS DR14\nObservational data',
               shape='ellipse',
               style='filled',
               fillcolor='#FFEBEE',
               fontcolor='#C62828',
               penwidth='0',
               fontsize='10')
        e.node('arxiv', 'arXiv API\nPaper database',
               shape='ellipse',
               style='filled',
               fillcolor='#FFEBEE',
               fontcolor='#C62828',
               penwidth='0',
               fontsize='10')
        e.node('llm', 'LLM APIs\n(Anthropic, Google, etc.)',
               shape='ellipse',
               style='filled',
               fillcolor='#FFEBEE',
               fontcolor='#C62828',
               penwidth='0',
               fontsize='10')

    # Main connections
    dot.edge('claude', 'server',
             label='MCP Protocol\n(stdio)',
             fontsize='10',
             color='#0D47A1',
             penwidth='2.5',
             arrowhead='vee')
    
    # Server to tools
    dot.edge('server', 't1', color='#2E7D32', penwidth='2', arrowhead='vee')
    dot.edge('server', 't2', color='#2E7D32', penwidth='2', arrowhead='vee')
    dot.edge('server', 't3', color='#2E7D32', penwidth='2', arrowhead='vee')
    dot.edge('server', 't4', color='#2E7D32', penwidth='2', arrowhead='vee')
    dot.edge('server', 't5', color='#2E7D32', penwidth='2', arrowhead='vee')
    dot.edge('server', 'a1', color='#4527A0', penwidth='2', arrowhead='vee')
    dot.edge('server', 'a2', color='#4527A0', penwidth='2', arrowhead='vee')

    # Tools use codes/
    dot.edge('t1', 'codes', style='dashed', label='uses', fontsize='9', color='#607D8B', penwidth='1', arrowhead='open')
    dot.edge('t2', 'codes', style='dashed', label='uses', fontsize='9', color='#607D8B', penwidth='1', arrowhead='open')
    dot.edge('t3', 'codes', style='dashed', label='uses', fontsize='9', color='#607D8B', penwidth='1', arrowhead='open')
    dot.edge('t4', 'codes', style='dashed', label='uses', fontsize='9', color='#607D8B', penwidth='1', arrowhead='open')

    # External dependencies
    dot.edge('t2', 'class', style='dashed', label='calls', fontsize='9', color='#B71C1C', penwidth='1', arrowhead='open')
    dot.edge('t3', 'eboss', style='dashed', label='reads', fontsize='9', color='#B71C1C', penwidth='1', arrowhead='open')
    dot.edge('a2', 'arxiv', style='dashed', label='queries', fontsize='9', color='#B71C1C', penwidth='1', arrowhead='open')
    dot.edge('a1', 'class', style='dashed', label='calls', fontsize='9', color='#B71C1C', penwidth='1', arrowhead='open')
    dot.edge('a1', 'llm', style='dashed', label='requires', fontsize='9', color='#B71C1C', penwidth='1', arrowhead='open')
    dot.edge('a2', 'llm', style='dashed', label='requires', fontsize='9', color='#B71C1C', penwidth='1', arrowhead='open')

    return dot


def power_spectrum_agent_internals():
    """
    Simplified generic view of multi-agent orchestration showing dataflow.
    """
    dot = Digraph('Power_Spectrum_Agent')
    dot.attr(rankdir='TB',
             fontsize='18',
             fontname='Helvetica-Bold',
             labelloc='t',
             label='Multi-Agent Orchestration: Generic Dataflow Pattern',
             bgcolor='#FAFAFA',
             pad='0.2',
             nodesep='0.3',
             ranksep='0.4',
             dpi='300')
    
    # Set default node attributes
    dot.node_attr.update(fontname='Helvetica', fontsize='12')
    dot.edge_attr.update(fontname='Helvetica', fontsize='11')

    # MCP Client
    dot.node('client', 'MCP Client',
             shape='box',
             style='rounded,filled',
             fillcolor='#1976D2',
             fontcolor='white',
             penwidth='0',
             fontsize='14')

    # Agent tool entry point
    dot.node('agent_tool', 'Agent Tool\n(e.g., power_spectrum_agent)',
             shape='box',
             style='rounded,filled',
             fillcolor='#7E57C2',
             fontcolor='white',
             penwidth='0',
             fontsize='12')

    # Orchestrator
    dot.node('orchestrator', 'Orchestrator Agent\n\nCoordinates sub-agents\nManages dataflow',
             shape='box',
             style='rounded,filled',
             fillcolor='#FF7043',
             fontcolor='white',
             penwidth='0',
             fontsize='12')

    # Sub-agents in a row
    dot.node('agent1', 'Sub-Agent 1\n\nData Loading',
             shape='box',
             style='rounded,filled',
             fillcolor='#26A69A',
             fontcolor='white',
             penwidth='0',
             fontsize='11')
    dot.node('agent2', 'Sub-Agent 2\n\nProcessing',
             shape='box',
             style='rounded,filled',
             fillcolor='#42A5F5',
             fontcolor='white',
             penwidth='0',
             fontsize='11')
    dot.node('agent3', 'Sub-Agent 3\n\nVisualization',
             shape='box',
             style='rounded,filled',
             fillcolor='#EC407A',
             fontcolor='white',
             penwidth='0',
             fontsize='11')

    # Results
    dot.node('results', 'Results',
             shape='box',
             style='rounded,filled',
             fillcolor='#FDD835',
             fontcolor='#424242',
             penwidth='0',
             fontsize='14')

    # Main flow
    dot.edge('client', 'agent_tool',
             label='1. Query',
             fontsize='11',
             penwidth='2.5',
             color='#0D47A1',
             arrowhead='vee',
             fontcolor='#0D47A1')
    dot.edge('agent_tool', 'orchestrator',
             label='2. Initialize',
             fontsize='11',
             color='#6A1B9A',
             penwidth='2',
             arrowhead='vee',
             fontcolor='#6A1B9A')

    # Orchestrator to sub-agents
    dot.edge('orchestrator', 'agent1',
             label='3. Task 1',
             fontsize='10',
             color='#00695C',
             penwidth='1.5',
             arrowhead='vee',
             fontcolor='#00695C')
    dot.edge('agent1', 'orchestrator',
             label='Data',
             fontsize='10',
             color='#00695C',
             style='dashed',
             penwidth='1.5',
             arrowhead='vee',
             fontcolor='#00695C')

    dot.edge('orchestrator', 'agent2',
             label='4. Task 2',
             fontsize='10',
             color='#0277BD',
             penwidth='1.5',
             arrowhead='vee',
             fontcolor='#0277BD')
    dot.edge('agent2', 'orchestrator',
             label='Results',
             fontsize='10',
             color='#0277BD',
             style='dashed',
             penwidth='1.5',
             arrowhead='vee',
             fontcolor='#0277BD')

    dot.edge('orchestrator', 'agent3',
             label='5. Task 3',
             fontsize='10',
             color='#AD1457',
             penwidth='1.5',
             arrowhead='vee',
             fontcolor='#AD1457')
    dot.edge('agent3', 'orchestrator',
             label='Outputs',
             fontsize='10',
             color='#AD1457',
             style='dashed',
             penwidth='1.5',
             arrowhead='vee',
             fontcolor='#AD1457')

    # Final results
    dot.edge('orchestrator', 'results',
             label='6. Assemble',
             fontsize='11',
             color='#E65100',
             penwidth='2',
             arrowhead='vee',
             fontcolor='#E65100')
    dot.edge('results', 'client',
             label='7. Return',
             fontsize='11',
             penwidth='2.5',
             color='#0D47A1',
             arrowhead='vee',
             fontcolor='#0D47A1')

    return dot


if __name__ == '__main__':
    print("Generating professional flowcharts with improved text size and spacing...")

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
    """
    High-level abstract architecture - generic and extensible view.
    Shows MCP-KE as a tool server pattern without specific implementation details.
    """
    dot = Digraph('Abstract_Architecture')
    dot.attr(rankdir='LR', 
             fontsize='16',
             fontname='Helvetica-Bold',
             labelloc='t',
             label='MCP-KE: Tool Server Pattern',
             bgcolor='#FAFAFA',
             pad='0.3',
             nodesep='0.4',
             ranksep='0.6',
             dpi='300')
    
    # Set default node attributes
    dot.node_attr.update(fontname='Helvetica', fontsize='12')
    dot.edge_attr.update(fontname='Helvetica')

    # MCP Client Layer
    with dot.subgraph(name='cluster_client') as c:
        c.attr(label='MCP Client Layer',
               style='rounded,filled',
               fillcolor='#E8F4FD',
               color='#1976D2',
               penwidth='2',
               fontsize='14',
               fontname='Helvetica-Bold')
        c.node('client', 'MCP Client\n\n(Any AI system or\napplication)',
               shape='box',
               style='rounded,filled',
               fillcolor='#2196F3',
               fontcolor='white',
               fontsize='12',
               penwidth='0')

    # MCP Server Core
    with dot.subgraph(name='cluster_server') as s:
        s.attr(label='MCP-KE Server',
               style='rounded,filled',
               fillcolor='#F1F8E9',
               color='#689F38',
               penwidth='2',
               fontsize='11',
               fontname='Helvetica-Bold')
        s.node('server', 'MCP Server\n\nAuto-discovery\nTool execution\nstdio communication',
               shape='box',
               style='rounded,filled',
               fillcolor='#8BC34A',
               fontcolor='white',
               penwidth='0')

        # Domain Tools
        with s.subgraph(name='cluster_domain') as d:
            d.attr(label='Domain Tools',
                   style='rounded,filled',
                   fillcolor='#FFF3E0',
                   color='#F57C00',
                   penwidth='1.5',
                   fontsize='10',
                   fontname='Helvetica-Bold')
            d.node('data_cat', 'Data Loading',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#FFB74D',
                   fontcolor='#424242',
                   penwidth='0')
            d.node('model_cat', 'Model Parameters',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#FFB74D',
                   fontcolor='#424242',
                   penwidth='0')
            d.node('analysis_cat', 'Analysis & Computation',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#FFB74D',
                   fontcolor='#424242',
                   penwidth='0')
            d.node('viz_cat', 'Visualization',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#FFB74D',
                   fontcolor='#424242',
                   penwidth='0')
            d.node('util_cat', 'Utilities',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#FFB74D',
                   fontcolor='#424242',
                   penwidth='0')

        # Agent Tools
        with s.subgraph(name='cluster_agent') as a:
            a.attr(label='Agent Tools',
                   style='rounded,filled',
                   fillcolor='#F3E5F5',
                   color='#7B1FA2',
                   penwidth='1.5',
                   fontsize='10',
                   fontname='Helvetica-Bold')
            a.node('agent1', 'power_spectrum_agent',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#BA68C8',
                   fontcolor='white',
                   penwidth='0')
            a.node('agent2', 'arxiv_agent',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#BA68C8',
                   fontcolor='white',
                   penwidth='0')
            a.node('agent_more', '...other agents',
                   shape='box',
                   style='rounded,dashed,filled',
                   fillcolor='#E1BEE7',
                   fontcolor='#4A148C',
                   penwidth='1.5',
                   color='#7B1FA2')

    # Core Implementation Layer
    with dot.subgraph(name='cluster_core') as core:
        core.attr(label='Core Domain Logic',
                  style='dashed,rounded',
                  color='#616161',
                  penwidth='1.5',
                  fontsize='10',
                  fontname='Helvetica')
        core.node('codes', 'Domain implementations\n(cosmology, analysis, viz...)',
                  shape='box',
                  style='rounded,filled',
                  fillcolor='#ECEFF1',
                  fontcolor='#37474F',
                  penwidth='0')

    # External Services
    with dot.subgraph(name='cluster_external') as e:
        e.attr(label='External Services',
               style='dashed,rounded',
               color='#D32F2F',
               penwidth='1.5',
               fontsize='10',
               fontname='Helvetica')
        e.node('llm_apis', 'LLM APIs',
               shape='ellipse',
               style='filled',
               fillcolor='#FFCDD2',
               fontcolor='#B71C1C',
               penwidth='0')
        e.node('data_apis', 'Data APIs\n(arXiv, etc.)',
               shape='ellipse',
               style='filled',
               fillcolor='#FFCDD2',
               fontcolor='#B71C1C',
               penwidth='0')
        e.node('compute', 'Compute Libraries',
               shape='ellipse',
               style='filled',
               fillcolor='#FFCDD2',
               fontcolor='#B71C1C',
               penwidth='0')

    # Main connections
    dot.edge('client', 'server',
             label='MCP\nProtocol',
             fontsize='9',
             color='#1565C0',
             penwidth='3',
             arrowhead='vee')

    # Server to tools
    dot.edge('server', 'data_cat', color='#558B2F', penwidth='2', arrowhead='vee')
    dot.edge('server', 'model_cat', color='#558B2F', penwidth='2', arrowhead='vee')
    dot.edge('server', 'analysis_cat', color='#558B2F', penwidth='2', arrowhead='vee')
    dot.edge('server', 'viz_cat', color='#558B2F', penwidth='2', arrowhead='vee')
    dot.edge('server', 'util_cat', color='#558B2F', penwidth='2', arrowhead='vee')
    dot.edge('server', 'agent1', color='#6A1B9A', penwidth='2', arrowhead='vee')
    dot.edge('server', 'agent2', color='#6A1B9A', penwidth='2', arrowhead='vee')
    dot.edge('server', 'agent_more', style='dashed', color='#6A1B9A', penwidth='1.5', arrowhead='vee')

    # Tools use core implementations
    dot.edge('data_cat', 'codes', style='dashed', label='use', fontsize='8', color='#757575', penwidth='1', arrowhead='open')
    dot.edge('model_cat', 'codes', style='dashed', fontsize='8', color='#757575', penwidth='1', arrowhead='open')
    dot.edge('analysis_cat', 'codes', style='dashed', fontsize='8', color='#757575', penwidth='1', arrowhead='open')
    dot.edge('viz_cat', 'codes', style='dashed', fontsize='8', color='#757575', penwidth='1', arrowhead='open')

    # External dependencies
    dot.edge('agent1', 'llm_apis', style='dashed', label='require', fontsize='8', color='#C62828', penwidth='1', arrowhead='open')
    dot.edge('agent2', 'llm_apis', style='dashed', fontsize='8', color='#C62828', penwidth='1', arrowhead='open')
    dot.edge('agent2', 'data_apis', style='dashed', fontsize='8', color='#C62828', penwidth='1', arrowhead='open')
    dot.edge('analysis_cat', 'compute', style='dashed', label='use', fontsize='8', color='#C62828', penwidth='1', arrowhead='open')


    # return dot


def mcp_overview():
    """
    High-level architecture showing MCP client-server relationship,
    domain tools vs agent tools, and external dependencies.
    """
    dot = Digraph('MCP_KE_Overview')
    dot.attr(rankdir='LR',
             fontsize='12',
             fontname='Helvetica',
             labelloc='t',
             label='MCP-KE Architecture: Tool Server with Domain & Agent Tools',
             bgcolor='#FAFAFA',
             pad='0.5',
             nodesep='0.7',
             ranksep='1.0',
             dpi='300')
    
    # Set default node attributes
    dot.node_attr.update(fontname='Helvetica', fontsize='9')
    dot.edge_attr.update(fontname='Helvetica')

    # MCP Client Layer
    with dot.subgraph(name='cluster_client') as c:
        c.attr(label='MCP Client Layer',
               style='rounded,filled',
               fillcolor='#E3F2FD',
               color='#1565C0',
               penwidth='2',
               fontsize='11',
               fontname='Helvetica-Bold')
        c.node('claude', 'Custom Agent\nor Claude Desktop',
               shape='box',
               style='rounded,filled',
               fillcolor='#1E88E5',
               fontcolor='white',
               penwidth='0')

    # MCP Server Core
    with dot.subgraph(name='cluster_server') as s:
        s.attr(label='mcp-ke MCP Server',
               style='rounded,filled',
               fillcolor='#E8F5E9',
               color='#43A047',
               penwidth='2',
               fontsize='11',
               fontname='Helvetica-Bold')
        s.node('server', 'mcp_server.py\n\n• Auto-discover @tool functions\n• Build MCP Tool schemas\n• Handle tool execution\n• stdio communication',
               shape='box',
               style='rounded,filled',
               fillcolor='#66BB6A',
               fontcolor='white',
               penwidth='0',
               fontsize='9')

        # Domain Tools
        with s.subgraph(name='cluster_domain') as d:
            d.attr(label='Domain Tools (tools/) - 16 tools',
                   style='rounded,filled',
                   fillcolor='#FFF8E1',
                   color='#FFA000',
                   penwidth='1.5',
                   fontsize='10',
                   fontname='Helvetica-Bold')
            d.node('t1', 'Model Parameters\nLCDM(), nu_mass()\nwCDM()',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#FFCA28',
                   fontcolor='#424242',
                   penwidth='0',
                   fontsize='8')
            d.node('t2', 'Power Spectrum\ncompute_power_spectrum()\ncompute_all_models()\ncompute_suppression_ratios()',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#FFCA28',
                   fontcolor='#424242',
                   penwidth='0',
                   fontsize='8')
            d.node('t3', 'Data Loading\nload_observational_data()\ncreate_theory_k_grid()',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#FFCA28',
                   fontcolor='#424242',
                   penwidth='0',
                   fontsize='8')
            d.node('t4', 'Visualization\nplot_power_spectra()\nplot_suppression_ratios()',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#FFCA28',
                   fontcolor='#424242',
                   penwidth='0',
                   fontsize='8')
            d.node('t5', 'Utilities\nsave/load_array()\nsave/load_dict()\nlist_agent_files()',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#FFCA28',
                   fontcolor='#424242',
                   penwidth='0',
                   fontsize='8')

        # Agent Tools
        with s.subgraph(name='cluster_agent') as a:
            a.attr(label='Agent Tools (agent_tools/) - 2 tools',
                   style='rounded,filled',
                   fillcolor='#EDE7F6',
                   color='#5E35B1',
                   penwidth='1.5',
                   fontsize='10',
                   fontname='Helvetica-Bold')
            a.node('a1', 'power_spectrum_agent\n\n4-agent orchestration:\n• orchestrator\n• data_agent\n• modeling_agent\n• viz_agent',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#9575CD',
                   fontcolor='white',
                   penwidth='0',
                   fontsize='8')
            a.node('a2', 'arxiv_agent\n\nSingle agent with tools:\n• search_arxiv\n• download_full_arxiv_paper\n• read_text_file',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#9575CD',
                   fontcolor='white',
                   penwidth='0',
                   fontsize='8')

    # Core Implementation Layer
    with dot.subgraph(name='cluster_core') as core:
        core.attr(label='Core Implementation (codes/)',
                  style='dashed,rounded',
                  color='#546E7A',
                  penwidth='1.5',
                  fontsize='10',
                  fontname='Helvetica')
        core.node('codes', 'cosmology_models.py\nanalysis.py\ndata.py\nviz.py',
                  shape='box',
                  style='rounded,filled',
                  fillcolor='#CFD8DC',
                  fontcolor='#263238',
                  penwidth='0',
                  fontsize='8')

    # External Services
    with dot.subgraph(name='cluster_external') as e:
        e.attr(label='External Services',
               style='dashed,rounded',
               color='#E53935',
               penwidth='1.5',
               fontsize='10',
               fontname='Helvetica')
        e.node('class', 'CLASS\nCosmology code',
               shape='ellipse',
               style='filled',
               fillcolor='#FFEBEE',
               fontcolor='#C62828',
               penwidth='0',
               fontsize='8')
        e.node('eboss', 'eBOSS DR14\nObservational data',
               shape='ellipse',
               style='filled',
               fillcolor='#FFEBEE',
               fontcolor='#C62828',
               penwidth='0',
               fontsize='8')
        e.node('arxiv', 'arXiv API\nPaper database',
               shape='ellipse',
               style='filled',
               fillcolor='#FFEBEE',
               fontcolor='#C62828',
               penwidth='0',
               fontsize='8')
        e.node('llm', 'LLM APIs\n(Anthropic, Google, etc.)',
               shape='ellipse',
               style='filled',
               fillcolor='#FFEBEE',
               fontcolor='#C62828',
               penwidth='0',
               fontsize='8')

    # Main connections
    dot.edge('claude', 'server',
             label='MCP Protocol\n(stdio)',
             fontsize='9',
             color='#0D47A1',
             penwidth='2.5',
             arrowhead='vee')
    
    # Server to tools
    dot.edge('server', 't1', color='#2E7D32', penwidth='2', arrowhead='vee')
    dot.edge('server', 't2', color='#2E7D32', penwidth='2', arrowhead='vee')
    dot.edge('server', 't3', color='#2E7D32', penwidth='2', arrowhead='vee')
    dot.edge('server', 't4', color='#2E7D32', penwidth='2', arrowhead='vee')
    dot.edge('server', 't5', color='#2E7D32', penwidth='2', arrowhead='vee')
    dot.edge('server', 'a1', color='#4527A0', penwidth='2', arrowhead='vee')
    dot.edge('server', 'a2', color='#4527A0', penwidth='2', arrowhead='vee')

    # Tools use codes/
    dot.edge('t1', 'codes', style='dashed', label='uses', fontsize='7', color='#607D8B', penwidth='1', arrowhead='open')
    dot.edge('t2', 'codes', style='dashed', label='uses', fontsize='7', color='#607D8B', penwidth='1', arrowhead='open')
    dot.edge('t3', 'codes', style='dashed', label='uses', fontsize='7', color='#607D8B', penwidth='1', arrowhead='open')
    dot.edge('t4', 'codes', style='dashed', label='uses', fontsize='7', color='#607D8B', penwidth='1', arrowhead='open')

    # External dependencies
    dot.edge('t2', 'class', style='dashed', label='calls', fontsize='7', color='#B71C1C', penwidth='1', arrowhead='open')
    dot.edge('t3', 'eboss', style='dashed', label='reads', fontsize='7', color='#B71C1C', penwidth='1', arrowhead='open')
    dot.edge('a2', 'arxiv', style='dashed', label='queries', fontsize='7', color='#B71C1C', penwidth='1', arrowhead='open')
    dot.edge('a1', 'class', style='dashed', label='calls', fontsize='7', color='#B71C1C', penwidth='1', arrowhead='open')
    dot.edge('a1', 'llm', style='dashed', label='requires', fontsize='7', color='#B71C1C', penwidth='1', arrowhead='open')
    dot.edge('a2', 'llm', style='dashed', label='requires', fontsize='7', color='#B71C1C', penwidth='1', arrowhead='open')

    return dot


def power_spectrum_agent_internals():
    """
    Simplified generic view of multi-agent orchestration showing dataflow.
    """
    dot = Digraph('Power_Spectrum_Agent')
    dot.attr(rankdir='TB',
             fontsize='12',
             fontname='Helvetica',
             labelloc='t',
             label='Multi-Agent Orchestration: Generic Dataflow Pattern',
             bgcolor='#FAFAFA',
             pad='0.5',
             nodesep='0.6',
             ranksep='0.8',
             dpi='300')
    
    # Set default node attributes
    dot.node_attr.update(fontname='Helvetica', fontsize='10')
    dot.edge_attr.update(fontname='Helvetica')

    # MCP Client
    dot.node('client', 'MCP Client',
             shape='box',
             style='rounded,filled',
             fillcolor='#1976D2',
             fontcolor='white',
             penwidth='0',
             fontsize='11')

    # Agent tool entry point
    dot.node('agent_tool', 'Agent Tool\n(e.g., power_spectrum_agent)',
             shape='box',
             style='rounded,filled',
             fillcolor='#7E57C2',
             fontcolor='white',
             penwidth='0',
             fontsize='10')

    # Orchestrator
    dot.node('orchestrator', 'Orchestrator Agent\n\nCoordinates sub-agents\nManages dataflow',
             shape='box',
             style='rounded,filled',
             fillcolor='#FF7043',
             fontcolor='white',
             penwidth='0',
             fontsize='10')

    # Sub-agents in a row
    dot.node('agent1', 'Sub-Agent 1\n\nData Loading',
             shape='box',
             style='rounded,filled',
             fillcolor='#26A69A',
             fontcolor='white',
             penwidth='0',
             fontsize='9')
    dot.node('agent2', 'Sub-Agent 2\n\nProcessing',
             shape='box',
             style='rounded,filled',
             fillcolor='#42A5F5',
             fontcolor='white',
             penwidth='0',
             fontsize='9')
    dot.node('agent3', 'Sub-Agent 3\n\nVisualization',
             shape='box',
             style='rounded,filled',
             fillcolor='#EC407A',
             fontcolor='white',
             penwidth='0',
             fontsize='9')

    # Results
    dot.node('results', 'Results',
             shape='box',
             style='rounded,filled',
             fillcolor='#FDD835',
             fontcolor='#424242',
             penwidth='0',
             fontsize='11')

    # Main flow
    dot.edge('client', 'agent_tool',
             label='1. Query',
             fontsize='9',
             penwidth='2.5',
             color='#0D47A1',
             arrowhead='vee',
             fontcolor='#0D47A1')
    dot.edge('agent_tool', 'orchestrator',
             label='2. Initialize',
             fontsize='9',
             color='#6A1B9A',
             penwidth='2',
             arrowhead='vee',
             fontcolor='#6A1B9A')

    # Orchestrator to sub-agents
    dot.edge('orchestrator', 'agent1',
             label='3. Task 1',
             fontsize='8',
             color='#00695C',
             penwidth='1.5',
             arrowhead='vee',
             fontcolor='#00695C')
    dot.edge('agent1', 'orchestrator',
             label='Data',
             fontsize='8',
             color='#00695C',
             style='dashed',
             penwidth='1.5',
             arrowhead='vee',
             fontcolor='#00695C')

    dot.edge('orchestrator', 'agent2',
             label='4. Task 2',
             fontsize='8',
             color='#0277BD',
             penwidth='1.5',
             arrowhead='vee',
             fontcolor='#0277BD')
    dot.edge('agent2', 'orchestrator',
             label='Results',
             fontsize='8',
             color='#0277BD',
             style='dashed',
             penwidth='1.5',
             arrowhead='vee',
             fontcolor='#0277BD')

    dot.edge('orchestrator', 'agent3',
             label='5. Task 3',
             fontsize='8',
             color='#AD1457',
             penwidth='1.5',
             arrowhead='vee',
             fontcolor='#AD1457')
    dot.edge('agent3', 'orchestrator',
             label='Outputs',
             fontsize='8',
             color='#AD1457',
             style='dashed',
             penwidth='1.5',
             arrowhead='vee',
             fontcolor='#AD1457')

    # Final results
    dot.edge('orchestrator', 'results',
             label='6. Assemble',
             fontsize='9',
             color='#E65100',
             penwidth='2',
             arrowhead='vee',
             fontcolor='#E65100')
    dot.edge('results', 'client',
             label='7. Return',
             fontsize='9',
             penwidth='2.5',
             color='#0D47A1',
             arrowhead='vee',
             fontcolor='#0D47A1')

    return dot


if __name__ == '__main__':
    print("Generating professional flowcharts...")

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