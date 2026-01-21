from graphviz import Digraph


def abstract_architecture():
    """
    High-level abstract architecture - generic and extensible view.
    Shows MCP-KE as a tool server pattern without specific implementation details.
    """
    dot = Digraph('Abstract_Architecture')
    dot.attr(rankdir='LR', 
             fontsize='20',
             fontname='Helvetica-Bold',
             labelloc='t',
             label='MCP-KE: Tool Server Pattern',
             bgcolor='#FAFAFA',
             pad='0.1',
             nodesep='0.2',
             ranksep='0.3',
             dpi='300')
    
    # Set default node attributes
    dot.node_attr.update(fontname='Helvetica', fontsize='14')
    dot.edge_attr.update(fontname='Helvetica', fontsize='12')

    # MCP Client Layer
    with dot.subgraph(name='cluster_client') as c:
        c.attr(label='MCP Client Layer',
               style='rounded,filled',
               fillcolor='#E8F4FD',
               color='#1976D2',
               penwidth='2',
               fontsize='16',
               fontname='Helvetica-Bold')
        c.node('client', 'MCP Client\n\n(Any AI system or\napplication)',
               shape='box',
               style='rounded,filled',
               fillcolor='#5E92F3',  # Lighter blue
               fontcolor='white',
               fontsize='14',
               penwidth='0')

    # MCP Server Core
    with dot.subgraph(name='cluster_server') as s:
        s.attr(label='MCP-KE Server',
               style='rounded,filled',
               fillcolor='#F1F8E9',
               color='#689F38',
               penwidth='2',
               fontsize='16',
               fontname='Helvetica-Bold')
        s.node('server', 'MCP Server\n\nAuto-discovery\nTool execution\nstdio communication',
               shape='box',
               style='rounded,filled',
               fillcolor='#81C784',  # Lighter green
               fontcolor='#1B5E20',  # Dark green text
               fontsize='14',
               penwidth='0')

        # Domain Tools
        with s.subgraph(name='cluster_domain') as d:
            d.attr(label='Domain Tools',
                   style='rounded,filled',
                   fillcolor='#FFF3E0',
                   color='#F57C00',
                   penwidth='1.5',
                   fontsize='14',
                   fontname='Helvetica-Bold')
            d.node('data_cat', 'Data Loading',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#FFB74D',
                   fontcolor='#424242',
                   fontsize='13',
                   penwidth='0')
            d.node('model_cat', 'Model Parameters',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#FFB74D',
                   fontcolor='#424242',
                   fontsize='13',
                   penwidth='0')
            d.node('analysis_cat', 'Analysis & Computation',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#FFB74D',
                   fontcolor='#424242',
                   fontsize='13',
                   penwidth='0')
            d.node('viz_cat', 'Visualization',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#FFB74D',
                   fontcolor='#424242',
                   fontsize='13',
                   penwidth='0')
            d.node('util_cat', 'Utilities',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#FFB74D',
                   fontcolor='#424242',
                   fontsize='13',
                   penwidth='0')

        # Agent Tools
        with s.subgraph(name='cluster_agent') as a:
            a.attr(label='Agent Tools',
                   style='rounded,filled',
                   fillcolor='#F3E5F5',
                   color='#7B1FA2',
                   penwidth='1.5',
                   fontsize='14',
                   fontname='Helvetica-Bold')
            a.node('agent1', 'power_spectrum_agent',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#AB47BC',  # Lighter purple
                   fontcolor='white',
                   fontsize='13',
                   penwidth='0')
            a.node('agent2', 'arxiv_agent',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#AB47BC',  # Lighter purple
                   fontcolor='white',
                   fontsize='13',
                   penwidth='0')
            a.node('agent_more', '...other agents',
                   shape='box',
                   style='rounded,dashed,filled',
                   fillcolor='#E1BEE7',
                   fontcolor='#4A148C',
                   fontsize='13',
                   penwidth='1.5',
                   color='#7B1FA2')

    # Core Implementation Layer
    with dot.subgraph(name='cluster_core') as core:
        core.attr(label='Core Domain Logic',
                  style='dashed,rounded',
                  color='#616161',
                  penwidth='1.5',
                  fontsize='14',
                  fontname='Helvetica')
        core.node('codes', 'Domain implementations\n(cosmology, analysis, viz...)',
                  shape='box',
                  style='rounded,filled',
                  fillcolor='#ECEFF1',
                  fontcolor='#37474F',
                  fontsize='13',
                  penwidth='0')

    # External Services
    with dot.subgraph(name='cluster_external') as e:
        e.attr(label='External Services',
               style='dashed,rounded',
               color='#D32F2F',
               penwidth='1.5',
               fontsize='14',
               fontname='Helvetica')
        e.node('llm_apis', 'LLM APIs',
               shape='ellipse',
               style='filled',
               fillcolor='#FFCDD2',
               fontcolor='#B71C1C',
               fontsize='13',
               penwidth='0')
        e.node('data_apis', 'Data APIs\n(arXiv, etc.)',
               shape='ellipse',
               style='filled',
               fillcolor='#FFCDD2',
               fontcolor='#B71C1C',
               fontsize='13',
               penwidth='0')
        e.node('compute', 'Compute Libraries',
               shape='ellipse',
               style='filled',
               fillcolor='#FFCDD2',
               fontcolor='#B71C1C',
               fontsize='13',
               penwidth='0')

    # Main connections
    dot.edge('client', 'server',
             label='MCP\nProtocol',
             fontsize='12',
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
    dot.edge('data_cat', 'codes', style='dashed', label='use', fontsize='11', color='#757575', penwidth='1', arrowhead='open')
    dot.edge('model_cat', 'codes', style='dashed', fontsize='11', color='#757575', penwidth='1', arrowhead='open')
    dot.edge('analysis_cat', 'codes', style='dashed', fontsize='11', color='#757575', penwidth='1', arrowhead='open')
    dot.edge('viz_cat', 'codes', style='dashed', fontsize='11', color='#757575', penwidth='1', arrowhead='open')

    # External dependencies
    dot.edge('agent1', 'llm_apis', style='dashed', label='require', fontsize='11', color='#C62828', penwidth='1', arrowhead='open')
    dot.edge('agent2', 'llm_apis', style='dashed', fontsize='11', color='#C62828', penwidth='1', arrowhead='open')
    dot.edge('agent2', 'data_apis', style='dashed', fontsize='11', color='#C62828', penwidth='1', arrowhead='open')
    dot.edge('analysis_cat', 'compute', style='dashed', label='use', fontsize='11', color='#C62828', penwidth='1', arrowhead='open')

    return dot


def mcp_overview():
    """
    High-level architecture showing MCP client-server relationship,
    domain tools vs agent tools, and external dependencies.
    """
    dot = Digraph('MCP_KE_Overview')
    dot.attr(rankdir='LR',
             fontsize='20',
             fontname='Helvetica-Bold',
             labelloc='t',
             label='MCP-KE Architecture: Tool Server with Domain & Agent Tools',
             bgcolor='#FAFAFA',
             pad='0.1',
             nodesep='0.15',
             ranksep='0.25',
             dpi='300')
    
    # Set default node attributes
    dot.node_attr.update(fontname='Helvetica', fontsize='13')
    dot.edge_attr.update(fontname='Helvetica', fontsize='12')

    # MCP Client Layer
    with dot.subgraph(name='cluster_client') as c:
        c.attr(label='MCP Client Layer',
               style='rounded,filled',
               fillcolor='#E3F2FD',
               color='#1565C0',
               penwidth='2',
               fontsize='16',
               fontname='Helvetica-Bold')
        c.node('claude', 'Custom Agent\nor Claude Desktop',
               shape='box',
               style='rounded,filled',
               fillcolor='#5E92F3',  # Lighter blue for better contrast
               fontcolor='white',
               fontsize='14',
               penwidth='0')

    # MCP Server Core
    with dot.subgraph(name='cluster_server') as s:
        s.attr(label='mcp-ke MCP Server',
               style='rounded,filled',
               fillcolor='#E8F5E9',
               color='#43A047',
               penwidth='2',
               fontsize='16',
               fontname='Helvetica-Bold')
        s.node('server', 'mcp_server.py\n\n• Auto-discover @tool functions\n• Build MCP Tool schemas\n• Handle tool execution\n• stdio communication',
               shape='box',
               style='rounded,filled',
               fillcolor='#81C784',  # Lighter green for better contrast
               fontcolor='#1B5E20',  # Dark green text instead of white
               penwidth='0',
               fontsize='13')

        # Domain Tools
        with s.subgraph(name='cluster_domain') as d:
            d.attr(label='Domain Tools (tools/) - 16 tools',
                   style='rounded,filled',
                   fillcolor='#FFF8E1',
                   color='#FFA000',
                   penwidth='1.5',
                   fontsize='14',
                   fontname='Helvetica-Bold')
            d.node('t1', 'Model Parameters\nLCDM(), nu_mass()\nwCDM()',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#FFCA28',
                   fontcolor='#424242',
                   penwidth='0',
                   fontsize='12')
            d.node('t2', 'Power Spectrum\ncompute_power_spectrum()\ncompute_all_models()\ncompute_suppression_ratios()',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#FFCA28',
                   fontcolor='#424242',
                   penwidth='0',
                   fontsize='12')
            d.node('t3', 'Data Loading\nload_observational_data()\ncreate_theory_k_grid()',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#FFCA28',
                   fontcolor='#424242',
                   penwidth='0',
                   fontsize='12')
            d.node('t4', 'Visualization\nplot_power_spectra()\nplot_suppression_ratios()',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#FFCA28',
                   fontcolor='#424242',
                   penwidth='0',
                   fontsize='12')
            d.node('t5', 'Utilities\nsave/load_array()\nsave/load_dict()\nlist_agent_files()',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#FFCA28',
                   fontcolor='#424242',
                   penwidth='0',
                   fontsize='12')

        # Agent Tools
        with s.subgraph(name='cluster_agent') as a:
            a.attr(label='Agent Tools (agent_tools/) - 2 tools',
                   style='rounded,filled',
                   fillcolor='#EDE7F6',
                   color='#5E35B1',
                   penwidth='1.5',
                   fontsize='14',
                   fontname='Helvetica-Bold')
            a.node('a1', 'power_spectrum_agent\n\n4-agent orchestration:\n• orchestrator\n• data_agent\n• modeling_agent\n• viz_agent',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#AB47BC',  # Lighter purple
                   fontcolor='white',
                   penwidth='0',
                   fontsize='12')
            a.node('a2', 'arxiv_agent\n\nSingle agent with tools:\n• search_arxiv\n• download_full_arxiv_paper\n• read_text_file',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#AB47BC',  # Lighter purple
                   fontcolor='white',
                   penwidth='0',
                   fontsize='12')

    # Core Implementation Layer
    with dot.subgraph(name='cluster_core') as core:
        core.attr(label='Core Implementation (codes/)',
                  style='dashed,rounded',
                  color='#546E7A',
                  penwidth='1.5',
                  fontsize='14',
                  fontname='Helvetica')
        core.node('codes', 'cosmology_models.py\nanalysis.py\ndata.py\nviz.py',
                  shape='box',
                  style='rounded,filled',
                  fillcolor='#CFD8DC',
                  fontcolor='#263238',
                  penwidth='0',
                  fontsize='12')

    # External Services
    with dot.subgraph(name='cluster_external') as e:
        e.attr(label='External Services',
               style='dashed,rounded',
               color='#E53935',
               penwidth='1.5',
               fontsize='14',
               fontname='Helvetica')
        e.node('class', 'CLASS\nCosmology code',
               shape='ellipse',
               style='filled',
               fillcolor='#FFEBEE',
               fontcolor='#C62828',
               penwidth='0',
               fontsize='12')
        e.node('eboss', 'eBOSS DR14\nObservational data',
               shape='ellipse',
               style='filled',
               fillcolor='#FFEBEE',
               fontcolor='#C62828',
               penwidth='0',
               fontsize='12')
        e.node('arxiv', 'arXiv API\nPaper database',
               shape='ellipse',
               style='filled',
               fillcolor='#FFEBEE',
               fontcolor='#C62828',
               penwidth='0',
               fontsize='12')
        e.node('llm', 'LLM APIs\n(Anthropic, Google, etc.)',
               shape='ellipse',
               style='filled',
               fillcolor='#FFEBEE',
               fontcolor='#C62828',
               penwidth='0',
               fontsize='12')

    # Main connections
    dot.edge('claude', 'server',
             label='MCP Protocol\n(stdio)',
             fontsize='12',
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
    dot.edge('t1', 'codes', style='dashed', label='uses', fontsize='11', color='#607D8B', penwidth='1', arrowhead='open')
    dot.edge('t2', 'codes', style='dashed', label='uses', fontsize='11', color='#607D8B', penwidth='1', arrowhead='open')
    dot.edge('t3', 'codes', style='dashed', label='uses', fontsize='11', color='#607D8B', penwidth='1', arrowhead='open')
    dot.edge('t4', 'codes', style='dashed', label='uses', fontsize='11', color='#607D8B', penwidth='1', arrowhead='open')

    # External dependencies
    dot.edge('t2', 'class', style='dashed', label='calls', fontsize='11', color='#B71C1C', penwidth='1', arrowhead='open')
    dot.edge('t3', 'eboss', style='dashed', label='reads', fontsize='11', color='#B71C1C', penwidth='1', arrowhead='open')
    dot.edge('a2', 'arxiv', style='dashed', label='queries', fontsize='11', color='#B71C1C', penwidth='1', arrowhead='open')
    dot.edge('a1', 'class', style='dashed', label='calls', fontsize='11', color='#B71C1C', penwidth='1', arrowhead='open')
    dot.edge('a1', 'llm', style='dashed', label='requires', fontsize='11', color='#B71C1C', penwidth='1', arrowhead='open')
    dot.edge('a2', 'llm', style='dashed', label='requires', fontsize='11', color='#B71C1C', penwidth='1', arrowhead='open')

    return dot


def power_spectrum_agent_internals():
    """
    Simplified generic view of multi-agent orchestration showing dataflow.
    """
    dot = Digraph('Power_Spectrum_Agent')
    dot.attr(rankdir='TB',
             fontsize='20',
             fontname='Helvetica-Bold',
             labelloc='t',
             label='Multi-Agent Orchestration: Generic Dataflow Pattern',
             bgcolor='#FAFAFA',
             pad='0.1',
             nodesep='0.2',
             ranksep='0.3',
             dpi='300')
    
    # Set default node attributes
    dot.node_attr.update(fontname='Helvetica', fontsize='14')
    dot.edge_attr.update(fontname='Helvetica', fontsize='12')

    # MCP Client
    dot.node('client', 'MCP Client',
             shape='box',
             style='rounded,filled',
             fillcolor='#5E92F3',  # Lighter blue
             fontcolor='white',
             penwidth='0',
             fontsize='16')

    # Agent tool entry point
    dot.node('agent_tool', 'Agent Tool\n(e.g., power_spectrum_agent)',
             shape='box',
             style='rounded,filled',
             fillcolor='#AB47BC',  # Lighter purple
             fontcolor='white',
             penwidth='0',
             fontsize='14')

    # Orchestrator
    dot.node('orchestrator', 'Orchestrator Agent\n\nCoordinates sub-agents\nManages dataflow',
             shape='box',
             style='rounded,filled',
             fillcolor='#FF8A65',  # Lighter orange
             fontcolor='white',
             penwidth='0',
             fontsize='14')

    # Sub-agents in a row
    dot.node('agent1', 'Sub-Agent 1\n\nData Loading',
             shape='box',
             style='rounded,filled',
             fillcolor='#4DB6AC',  # Lighter teal
             fontcolor='white',
             penwidth='0',
             fontsize='13')
    dot.node('agent2', 'Sub-Agent 2\n\nProcessing',
             shape='box',
             style='rounded,filled',
             fillcolor='#64B5F6',  # Lighter blue
             fontcolor='white',
             penwidth='0',
             fontsize='13')
    dot.node('agent3', 'Sub-Agent 3\n\nVisualization',
             shape='box',
             style='rounded,filled',
             fillcolor='#F06292',  # Lighter pink
             fontcolor='white',
             penwidth='0',
             fontsize='13')

    # Results
    dot.node('results', 'Results',
             shape='box',
             style='rounded,filled',
             fillcolor='#FDD835',
             fontcolor='#424242',
             penwidth='0',
             fontsize='16')

    # Main flow
    dot.edge('client', 'agent_tool',
             label='1. Query',
             fontsize='12',
             penwidth='2.5',
             color='#0D47A1',
             arrowhead='vee',
             fontcolor='#0D47A1')
    dot.edge('agent_tool', 'orchestrator',
             label='2. Initialize',
             fontsize='12',
             color='#6A1B9A',
             penwidth='2',
             arrowhead='vee',
             fontcolor='#6A1B9A')

    # Orchestrator to sub-agents
    dot.edge('orchestrator', 'agent1',
             label='3. Task 1',
             fontsize='11',
             color='#00695C',
             penwidth='1.5',
             arrowhead='vee',
             fontcolor='#00695C')
    dot.edge('agent1', 'orchestrator',
             label='Data',
             fontsize='11',
             color='#00695C',
             style='dashed',
             penwidth='1.5',
             arrowhead='vee',
             fontcolor='#00695C')

    dot.edge('orchestrator', 'agent2',
             label='4. Task 2',
             fontsize='11',
             color='#0277BD',
             penwidth='1.5',
             arrowhead='vee',
             fontcolor='#0277BD')
    dot.edge('agent2', 'orchestrator',
             label='Results',
             fontsize='11',
             color='#0277BD',
             style='dashed',
             penwidth='1.5',
             arrowhead='vee',
             fontcolor='#0277BD')

    dot.edge('orchestrator', 'agent3',
             label='5. Task 3',
             fontsize='11',
             color='#AD1457',
             penwidth='1.5',
             arrowhead='vee',
             fontcolor='#AD1457')
    dot.edge('agent3', 'orchestrator',
             label='Outputs',
             fontsize='11',
             color='#AD1457',
             style='dashed',
             penwidth='1.5',
             arrowhead='vee',
             fontcolor='#AD1457')

    # Final results
    dot.edge('orchestrator', 'results',
             label='6. Assemble',
             fontsize='12',
             color='#E65100',
             penwidth='2',
             arrowhead='vee',
             fontcolor='#E65100')
    dot.edge('results', 'client',
             label='7. Return',
             fontsize='12',
             penwidth='2.5',
             color='#0D47A1',
             arrowhead='vee',
             fontcolor='#0D47A1')

    return dot


def lya_flowchart():
    """
    Lyman-alpha forest analysis workflow showing forward model and inference pipeline.
    Shows the flow from cosmological parameters through simulation to parameter inference,
    with both ideal-space and observation-like paths.
    
    Layout matches the original reference with horizontal flow and two-branch structure.
    """
    dot = Digraph('Lya_Workflow')
    dot.attr(rankdir='LR',
             fontsize='18',
             fontname='Helvetica-Bold',
             labelloc='t',
             label='Lyman-α Forest Analysis Pipeline',
             bgcolor='#FAFAFA',
             pad='0.5',
             nodesep='0.25',
             ranksep='0.45',
             dpi='300')
    
    # Set default node attributes  
    dot.node_attr.update(fontname='Helvetica', fontsize='11')
    dot.edge_attr.update(fontname='Helvetica', fontsize='10')

    # ========== Forward Model Cluster ==========
    with dot.subgraph(name='cluster_forward') as fm:
        fm.attr(label='Forward Model',
                style='dashed,rounded',
                color='#546E7A',
                penwidth='2',
                fontsize='14',
                fontname='Helvetica-Bold',
                labeljust='l',
                margin='15')
        
        # Main simulation chain
        fm.node('cosmo', 'Cosmology\nT(k; θDM)',
                shape='box',
                style='rounded,filled',
                fillcolor='#5E92F3',
                fontcolor='white',
                penwidth='0')
        
        fm.node('ics', 'Initial\nConditions',
                shape='box',
                style='rounded,filled',
                fillcolor='#81C784',
                fontcolor='#1B5E20',
                penwidth='0')
        
        fm.node('hydro', 'Hydro\nSimulation',
                shape='box',
                style='rounded,filled',
                fillcolor='#81C784',
                fontcolor='#1B5E20',
                penwidth='0')
        
        # Observation operator (top branch - dashed path)
        fm.node('obs_op', 'Observation\nOperator\nnoise/masks/etc',
                shape='box',
                style='rounded,filled',
                fillcolor='#AB47BC',
                fontcolor='white',
                penwidth='0')
        
        # Obs-like statistics (top branch end)
        fm.node('obslike', 'Obs-like\nP̂₁D, PDF, WST',
                shape='box',
                style='rounded,filled',
                fillcolor='#F06292',
                fontcolor='white',
                penwidth='0')
        
        # Spectra extraction (bottom branch - solid path)
        fm.node('spectra', 'Spectra\nExtraction\nτHI, F(v)',
                shape='box',
                style='rounded,filled',
                fillcolor='#FFB74D',
                fontcolor='#424242',
                penwidth='0')
        
        # Ideal-space path (bottom branch)
        fm.node('ideal', 'Ideal-space\nP₁D, PDF, WST',
                shape='box',
                style='rounded,filled',
                fillcolor='#4DB6AC',
                fontcolor='white',
                penwidth='0')

    # ========== Inference Cluster ==========
    with dot.subgraph(name='cluster_inference') as inf:
        inf.attr(label='Inference',
                 style='dashed,rounded',
                 color='#E53935',
                 penwidth='2',
                 fontsize='14',
                 fontname='Helvetica-Bold',
                 labeljust='l',
                 margin='15')
        
        inf.node('emulator', 'Emulator\nθ ↦ m(θ)',
                 shape='box',
                 style='rounded,filled',
                 fillcolor='#FF8A65',
                 fontcolor='white',
                 penwidth='0')
        
        inf.node('likelihood', 'Likelihood\nd vs m(θ)',
                 shape='box',
                 style='rounded,filled',
                 fillcolor='#FF8A65',
                 fontcolor='white',
                 penwidth='0')
        
        inf.node('posterior', 'Posterior\np(θ | d)',
                 shape='box',
                 style='rounded,filled',
                 fillcolor='#FDD835',
                 fontcolor='#424242',
                 penwidth='0')
        
        inf.node('data', 'Data\nDESI, high-res, ...',
                 shape='box',
                 style='rounded,filled',
                 fillcolor='#ECEFF1',
                 fontcolor='#37474F',
                 penwidth='1',
                 color='#546E7A')

    # ========== Layout control ==========
    # Use invisible edges to control vertical positioning
    # Top row: obs_op, obslike (dashed path)
    # Bottom row: spectra, ideal (solid path)
    
    # Push spectra and ideal below obs_op and obslike
    dot.edge('spectra', 'obs_op', style='invis')
    dot.edge('ideal', 'obslike', style='invis')
    dot.edge('likelihood', 'data', style='invis')

    # ========== Main flow edges ==========
    # Forward model chain
    dot.edge('cosmo', 'ics', color='#424242', penwidth='1.5', arrowhead='vee')
    dot.edge('ics', 'hydro', color='#424242', penwidth='1.5', arrowhead='vee')
    
    # Branch to obs_op -> obslike (dashed - top path)  
    dot.edge('hydro', 'obs_op', style='dashed', color='#424242', penwidth='1.5', arrowhead='vee')
    dot.edge('obs_op', 'obslike', style='dashed', color='#424242', penwidth='1.5', arrowhead='vee')
    
    # Branch to spectra -> ideal (solid - bottom path)
    dot.edge('hydro', 'spectra', color='#424242', penwidth='1.5', arrowhead='vee')
    dot.edge('spectra', 'ideal', color='#424242', penwidth='1.5', arrowhead='vee')
    
    # Both paths to emulator
    dot.edge('obslike', 'emulator', style='dashed', color='#424242', penwidth='1.5', arrowhead='vee')
    dot.edge('ideal', 'emulator', color='#424242', penwidth='1.5', arrowhead='vee')
    
    # Inference chain
    dot.edge('emulator', 'likelihood', color='#424242', penwidth='1.5', arrowhead='vee')
    dot.edge('likelihood', 'posterior', color='#424242', penwidth='1.5', arrowhead='vee')
    dot.edge('data', 'likelihood', color='#424242', penwidth='1.5', arrowhead='vee')

    # ========== Legend ==========
    with dot.subgraph(name='cluster_legend') as leg:
        leg.attr(rank='sink', label='', style='invis', margin='0')
        leg.node('l1', '', shape='point', width='0.01')
        leg.node('l2', '', shape='point', width='0.01')
        leg.node('l3', '', shape='point', width='0.01')
        leg.node('l4', '', shape='point', width='0.01')
    
    dot.edge('l1', 'l2', 
             label='  Stage 0 (ideal-space)',
             color='#424242', penwidth='1.5', arrowhead='vee',
             fontsize='10', fontcolor='#424242')
    dot.edge('l3', 'l4',
             label='  Stage 0B+ (obs-like)', 
             style='dashed', color='#424242', penwidth='1.5', arrowhead='vee',
             fontsize='10', fontcolor='#424242')

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

    d3 = lya_flowchart()
    d3.render('lya_flowchart', format='png', cleanup=True)
    print("✓ Generated lya_flowchart.png")

    print("\nAll flowcharts generated successfully!")