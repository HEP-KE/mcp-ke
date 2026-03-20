from graphviz import Digraph


def generic_architecture():
    """
    Generic physics architecture with two MCP servers:
    - Analysis-MCP for computation tools
    - Knowledge-Base-MCP for document retrieval
    Connects to Genesis Infrastructure for LLM APIs.
    """
    dot = Digraph('Generic_Architecture')
    dot.attr(rankdir='LR',
             fontsize='20',
             fontname='Helvetica-Bold',
             labelloc='t',
             label='MCP Tool Server Pattern: Multi-Server Architecture',
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
               fillcolor='#5E92F3',
               fontcolor='white',
               fontsize='14',
               penwidth='0')

    # Analysis-MCP Server
    with dot.subgraph(name='cluster_analysis') as s:
        s.attr(label='Analysis-MCP Server',
               style='rounded,filled',
               fillcolor='#F1F8E9',
               color='#689F38',
               penwidth='2',
               fontsize='16',
               fontname='Helvetica-Bold')
        s.node('analysis_server', 'MCP Server\n\nAuto-discovery\nTool execution\nstdio communication',
               shape='box',
               style='rounded,filled',
               fillcolor='#81C784',
               fontcolor='#1B5E20',
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
            a.node('agent1', 'arxiv_agent',
                   shape='box',
                   style='rounded,filled',
                   fillcolor='#AB47BC',
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

    # Knowledge-Base-MCP Server
    with dot.subgraph(name='cluster_kb') as kb:
        kb.attr(label='Knowledge-Base-MCP Server',
                style='rounded,filled',
                fillcolor='#E8F5E9',
                color='#4CAF50',
                penwidth='2',
                fontsize='16',
                fontname='Helvetica-Bold')
        kb.node('kb_server', 'MCP Server\n\nDocument retrieval\nSemantic search\nstdio communication',
                shape='box',
                style='rounded,filled',
                fillcolor='#66BB6A',
                fontcolor='#1B5E20',
                fontsize='14',
                penwidth='0')

        # KB Tools
        with kb.subgraph(name='cluster_kb_tools') as kbt:
            kbt.attr(label='Knowledge Tools',
                     style='rounded,filled',
                     fillcolor='#E3F2FD',
                     color='#1976D2',
                     penwidth='1.5',
                     fontsize='14',
                     fontname='Helvetica-Bold')
            kbt.node('kb_search', 'Search & Retrieval',
                     shape='box',
                     style='rounded,filled',
                     fillcolor='#64B5F6',
                     fontcolor='#0D47A1',
                     fontsize='13',
                     penwidth='0')
            kbt.node('kb_docs', 'Document Storage',
                     shape='box',
                     style='rounded,filled',
                     fillcolor='#64B5F6',
                     fontcolor='#0D47A1',
                     fontsize='13',
                     penwidth='0')
            kbt.node('kb_embed', 'Embeddings',
                     shape='box',
                     style='rounded,filled',
                     fillcolor='#64B5F6',
                     fontcolor='#0D47A1',
                     fontsize='13',
                     penwidth='0')
            kbt.node('kb_summary', 'Summarization',
                     shape='box',
                     style='rounded,filled',
                     fillcolor='#64B5F6',
                     fontcolor='#0D47A1',
                     fontsize='13',
                     penwidth='0')

    # Genesis Infrastructure
    with dot.subgraph(name='cluster_genesis') as g:
        g.attr(label='Genesis Infrastructure',
               style='dashed,rounded',
               color='#D32F2F',
               penwidth='1.5',
               fontsize='14',
               fontname='Helvetica')
        g.node('llm_apis', 'AmSC LLM APIs',
               shape='ellipse',
               style='filled',
               fillcolor='#FFCDD2',
               fontcolor='#B71C1C',
               fontsize='13',
               penwidth='0')
        g.node('data_apis', 'Data APIs\n(arXiv, etc.)',
               shape='ellipse',
               style='filled',
               fillcolor='#FFCDD2',
               fontcolor='#B71C1C',
               fontsize='13',
               penwidth='0')
        g.node('compute', 'Compute Libraries',
               shape='ellipse',
               style='filled',
               fillcolor='#FFCDD2',
               fontcolor='#B71C1C',
               fontsize='13',
               penwidth='0')

    # Main connections - Client to servers
    dot.edge('client', 'analysis_server',
             label='MCP\nProtocol',
             fontsize='12',
             color='#1565C0',
             penwidth='3',
             arrowhead='vee')
    dot.edge('client', 'kb_server',
             label='MCP\nProtocol',
             fontsize='12',
             color='#1565C0',
             penwidth='3',
             arrowhead='vee')

    # Analysis server to tools
    dot.edge('analysis_server', 'data_cat', color='#558B2F', penwidth='2', arrowhead='vee')
    dot.edge('analysis_server', 'model_cat', color='#558B2F', penwidth='2', arrowhead='vee')
    dot.edge('analysis_server', 'analysis_cat', color='#558B2F', penwidth='2', arrowhead='vee')
    dot.edge('analysis_server', 'viz_cat', color='#558B2F', penwidth='2', arrowhead='vee')
    dot.edge('analysis_server', 'util_cat', color='#558B2F', penwidth='2', arrowhead='vee')
    dot.edge('analysis_server', 'agent1', color='#6A1B9A', penwidth='2', arrowhead='vee')
    dot.edge('analysis_server', 'agent_more', style='dashed', color='#6A1B9A', penwidth='1.5', arrowhead='vee')

    # KB server to tools
    dot.edge('kb_server', 'kb_search', color='#1565C0', penwidth='2', arrowhead='vee')
    dot.edge('kb_server', 'kb_docs', color='#1565C0', penwidth='2', arrowhead='vee')
    dot.edge('kb_server', 'kb_embed', color='#1565C0', penwidth='2', arrowhead='vee')
    dot.edge('kb_server', 'kb_summary', color='#1565C0', penwidth='2', arrowhead='vee')

    # External dependencies
    dot.edge('agent1', 'llm_apis', style='dashed', label='require', fontsize='11', color='#C62828', penwidth='1', arrowhead='open')
    dot.edge('agent1', 'data_apis', style='dashed', fontsize='11', color='#C62828', penwidth='1', arrowhead='open')
    dot.edge('analysis_cat', 'compute', style='dashed', label='use', fontsize='11', color='#C62828', penwidth='1', arrowhead='open')
    dot.edge('kb_embed', 'llm_apis', style='dashed', label='require', fontsize='11', color='#C62828', penwidth='1', arrowhead='open')
    dot.edge('kb_summary', 'llm_apis', style='dashed', fontsize='11', color='#C62828', penwidth='1', arrowhead='open')

    return dot


def mu2e_architecture():
    """
    Mu2e Run-1 architecture with simplified 3-color scheme:
    - Blue: HEP-KE products (MCP Client, Analysis-MCP Server, Knowledge-Base-MCP Server)
    - Green: Phase-1 Deliverables (Domain Tools, Agent Tools, Documentation, HPC/Mu2e Resources)
    - Red: Genesis Infrastructure
    """
    dot = Digraph('Mu2e_Architecture')
    dot.attr(rankdir='LR',
             fontsize='20',
             fontname='Helvetica-Bold',
             labelloc='t',
             label='KE: Agentic Framework Example',
             bgcolor='#FAFAFA',
             pad='0.1',
             nodesep='0.2',
             ranksep='0.3',
             dpi='300')

    # ===========================================
    # COLOR SCHEME
    # ===========================================
    # KE (Blue theme)
    KE_CLUSTER_BG = '#E3F2FD'       # Light blue background
    KE_CLUSTER_BORDER = '#1565C0'   # Dark blue border
    KE_NODE_BG = '#1976D2'          # Blue node
    KE_NODE_BG_LIGHT = '#64B5F6'    # Light blue node
    KE_TEXT = 'white'
    KE_TEXT_DARK = '#0D47A1'

    # Phase-1 Deliverables (Green theme)
    P1_CLUSTER_BG = '#E8F5E9'       # Light green background
    P1_CLUSTER_BORDER = '#2E7D32'   # Dark green border
    P1_NODE_BG = '#43A047'          # Green node
    P1_NODE_BG_LIGHT = '#81C784'    # Light green node
    P1_TEXT = 'white'
    P1_TEXT_DARK = '#1B5E20'

    # Genesis Infrastructure (Red theme)
    GEN_CLUSTER_BG = '#FFEBEE'      # Light red background
    GEN_CLUSTER_BORDER = '#C62828'  # Dark red border
    GEN_NODE_BG = '#EF5350'         # Red node
    GEN_NODE_BG_LIGHT = '#FFCDD2'   # Light red node
    GEN_TEXT = 'white'
    GEN_TEXT_DARK = '#B71C1C'

    # Set default node attributes
    dot.node_attr.update(fontname='Helvetica', fontsize='14')
    dot.edge_attr.update(fontname='Helvetica', fontsize='12')

    # ===========================================
    # LEGEND (Components) - above MCP Client Layer
    # ===========================================
    legend_label = '''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="4">
        <TR><TD COLSPAN="1"><B>Components</B></TD></TR>
        <TR><TD BGCOLOR="#1976D2"><FONT COLOR="white" POINT-SIZE="12">HEP-KE products</FONT></TD></TR>
        <TR><TD BGCOLOR="#43A047"><FONT COLOR="white" POINT-SIZE="12">Phase-1 deliverables</FONT></TD></TR>
        <TR><TD BGCOLOR="#EF5350"><FONT COLOR="white" POINT-SIZE="12">Genesis Infrastructure</FONT></TD></TR>
    </TABLE>>'''

    # ===========================================
    # KE: MCP Client Layer (Blue) with legend above
    # ===========================================
    # Wrapper cluster for legend + client to keep them together on the left
    # Increase margin to push legend higher (e.g., margin='20' for more space at top)
    with dot.subgraph(name='cluster_left') as left:
        left.attr(label='',
                  style='invis',
                  margin='36')

        # Legend above client
        left.node('legend', legend_label,
                  shape='none',
                  fontsize='14')

        with left.subgraph(name='cluster_client') as c:
            c.attr(label='MCP Client Layer',
                   style='rounded,filled',
                   fillcolor=KE_CLUSTER_BG,
                   color=KE_CLUSTER_BORDER,
                   penwidth='2',
                   fontsize='16',
                   fontname='Helvetica-Bold')
            c.node('client', 'MCP Client\n\n(Any AI system or\napplication)',
                   shape='box',
                   style='rounded,filled',
                   fillcolor=KE_NODE_BG,
                   fontcolor=KE_TEXT,
                   fontsize='14',
                   penwidth='0')

    # ===========================================
    # HEP-KE: Analysis-MCP Server (Blue cluster with green tools inside)
    # ===========================================
    with dot.subgraph(name='cluster_analysis') as s:
        s.attr(label='Analysis-MCP Server',
               style='rounded,filled',
               fillcolor=KE_CLUSTER_BG,
               color=KE_CLUSTER_BORDER,
               penwidth='2',
               fontsize='16',
               fontname='Helvetica-Bold')
        s.node('analysis_server', 'MCP Server\n\nAuto-discovery\nTool execution\nstdio communication',
               shape='box',
               style='rounded,filled',
               fillcolor=KE_NODE_BG,
               fontcolor=KE_TEXT,
               fontsize='14',
               penwidth='0')

        # Domain Tools (Green - Phase-1)
        with s.subgraph(name='cluster_domain') as d:
            d.attr(label='Domain Tools',
                   style='rounded,filled',
                   fillcolor='#C8E6C9',
                   color=P1_CLUSTER_BORDER,
                   penwidth='1.5',
                   fontsize='14',
                   fontname='Helvetica-Bold')
            d.node('analysis_fw', 'Analysis\nFramework',
                   shape='box',
                   style='rounded,filled',
                   fillcolor=P1_NODE_BG_LIGHT,
                   fontcolor=P1_TEXT_DARK,
                   fontsize='13',
                   penwidth='0')
            d.node('beam_sim', 'Beam and Detector\nSimulation',
                   shape='box',
                   style='rounded,filled',
                   fillcolor=P1_NODE_BG_LIGHT,
                   fontcolor=P1_TEXT_DARK,
                   fontsize='13',
                   penwidth='0')
            d.node('data_loading', 'Data Loading\nand Bookkeeping',
                   shape='box',
                   style='rounded,filled',
                   fillcolor=P1_NODE_BG_LIGHT,
                   fontcolor=P1_TEXT_DARK,
                   fontsize='13',
                   penwidth='0')
            d.node('viz_cat', 'Visualization',
                   shape='box',
                   style='rounded,filled',
                   fillcolor=P1_NODE_BG_LIGHT,
                   fontcolor=P1_TEXT_DARK,
                   fontsize='13',
                   penwidth='0')

        # Agent Tools
        with s.subgraph(name='cluster_agent') as a:
            a.attr(label='Agent Tools',
                   style='rounded,filled',
                   fillcolor='#A5D6A7',
                   color=P1_CLUSTER_BORDER,
                   penwidth='1.5',
                   fontsize='14',
                   fontname='Helvetica-Bold')
            a.node('agent1', 'optimization_agent',
                   shape='box',
                   style='rounded,filled',
                   fillcolor=P1_NODE_BG,
                   fontcolor=P1_TEXT,
                   fontsize='13',
                   penwidth='0')
            a.node('agent_more', '...other agents',
                   shape='box',
                   style='rounded,dashed,filled',
                   fillcolor=P1_NODE_BG_LIGHT,
                   fontcolor=P1_TEXT_DARK,
                   fontsize='13',
                   penwidth='1.5',
                   color=P1_CLUSTER_BORDER)

    # ===========================================
    # KE: Knowledge-Base-MCP Server (Blue)
    # ===========================================
    with dot.subgraph(name='cluster_kb') as kb:
        kb.attr(label='Knowledge-Base-MCP Server',
                style='rounded,filled',
                fillcolor=KE_CLUSTER_BG,
                color=KE_CLUSTER_BORDER,
                penwidth='2',
                fontsize='16',
                fontname='Helvetica-Bold')
        kb.node('kb_server', 'MCP Server\n\nDocument retrieval\nSemantic search\nstdio communication',
                shape='box',
                style='rounded,filled',
                fillcolor=KE_NODE_BG,
                fontcolor=KE_TEXT,
                fontsize='14',
                penwidth='0')

        # KB Tools
        with kb.subgraph(name='cluster_kb_tools') as kbt:
            kbt.attr(label='Knowledge Tools',
                     style='rounded,filled',
                     fillcolor='#BBDEFB',
                     color=KE_CLUSTER_BORDER,
                     penwidth='1.5',
                     fontsize='14',
                     fontname='Helvetica-Bold')
            kbt.node('kb_embed', 'Embeddings',
                     shape='box',
                     style='rounded,filled',
                     fillcolor=KE_NODE_BG_LIGHT,
                     fontcolor=KE_TEXT_DARK,
                     fontsize='13',
                     penwidth='0')
            kbt.node('kb_docs', 'Documentation',
                     shape='box',
                     style='rounded,filled',
                     fillcolor=P1_NODE_BG_LIGHT,
                     fontcolor=P1_TEXT_DARK,
                     fontsize='13',
                     penwidth='0')
            kbt.node('kb_summary', 'Summarization',
                     shape='box',
                     style='rounded,filled',
                     fillcolor=KE_NODE_BG_LIGHT,
                     fontcolor=KE_TEXT_DARK,
                     fontsize='13',
                     penwidth='0')

    # ===========================================
    # PHASE-1: HPC/Mu2e Resources (Green)
    # ===========================================
    with dot.subgraph(name='cluster_mu2e_data') as md:
        md.attr(label='HPC/Mu2e\nResources',
                style='dashed,rounded',
                color=P1_CLUSTER_BORDER,
                fillcolor=P1_CLUSTER_BG,
                penwidth='1.5',
                fontsize='14',
                fontname='Helvetica')
        md.node('sims', 'Simulations',
                shape='ellipse',
                style='filled',
                fillcolor=P1_NODE_BG_LIGHT,
                fontcolor=P1_TEXT_DARK,
                fontsize='13',
                penwidth='0')
        md.node('fermi_data', 'Fermi Data\nHandling',
                shape='ellipse',
                style='filled',
                fillcolor=P1_NODE_BG_LIGHT,
                fontcolor=P1_TEXT_DARK,
                fontsize='13',
                penwidth='0')

    # ===========================================
    # GENESIS: Infrastructure (Red)
    # ===========================================
    with dot.subgraph(name='cluster_genesis') as g:
        g.attr(label='Genesis Infrastructure',
               style='dashed,rounded',
               color=GEN_CLUSTER_BORDER,
               fillcolor=GEN_CLUSTER_BG,
               penwidth='1.5',
               fontsize='14',
               fontname='Helvetica')
        g.node('llm_apis', 'AmSC LLM APIs',
               shape='ellipse',
               style='filled',
               fillcolor=GEN_NODE_BG_LIGHT,
               fontcolor=GEN_TEXT_DARK,
               fontsize='13',
               penwidth='0')
        g.node('data_apis', 'Data APIs',
               shape='ellipse',
               style='filled',
               fillcolor=GEN_NODE_BG_LIGHT,
               fontcolor=GEN_TEXT_DARK,
               fontsize='13',
               penwidth='0')

    # ===========================================
    # EDGES
    # ===========================================
    # Main connections - Client to servers
    dot.edge('client', 'analysis_server',
             label='MCP\nProtocol',
             fontsize='12',
             color=KE_CLUSTER_BORDER,
             penwidth='3',
             arrowhead='vee')
    dot.edge('client', 'kb_server',
             label='MCP\nProtocol',
             fontsize='12',
             color=KE_CLUSTER_BORDER,
             penwidth='3',
             arrowhead='vee')

    # Analysis server to tools (green edges for Phase-1 tools)
    dot.edge('analysis_server', 'analysis_fw', color=P1_CLUSTER_BORDER, penwidth='2', arrowhead='vee')
    dot.edge('analysis_server', 'beam_sim', color=P1_CLUSTER_BORDER, penwidth='2', arrowhead='vee')
    dot.edge('analysis_server', 'data_loading', color=P1_CLUSTER_BORDER, penwidth='2', arrowhead='vee')
    dot.edge('analysis_server', 'viz_cat', color=P1_CLUSTER_BORDER, penwidth='2', arrowhead='vee')
    dot.edge('analysis_server', 'agent1', color=P1_CLUSTER_BORDER, penwidth='2', arrowhead='vee')
    dot.edge('analysis_server', 'agent_more', style='dashed', color=P1_CLUSTER_BORDER, penwidth='1.5', arrowhead='vee')

    # KB server to tools
    dot.edge('kb_server', 'kb_embed', color=KE_CLUSTER_BORDER, penwidth='2', arrowhead='vee')
    dot.edge('kb_server', 'kb_docs', color=KE_CLUSTER_BORDER, penwidth='2', arrowhead='vee')
    dot.edge('kb_server', 'kb_summary', color=KE_CLUSTER_BORDER, penwidth='2', arrowhead='vee')

    # Mu2e data dependencies (Phase-1 color)
    dot.edge('beam_sim', 'sims', style='dashed', fontsize='11', color=P1_CLUSTER_BORDER, penwidth='1', arrowhead='open')
    dot.edge('data_loading', 'fermi_data', style='dashed', fontsize='11', color=P1_CLUSTER_BORDER, penwidth='1', arrowhead='open')

    # Genesis infrastructure dependencies (Red color)
    dot.edge('agent1', 'llm_apis', style='dashed', label='require', fontsize='11', color=GEN_CLUSTER_BORDER, penwidth='1', arrowhead='open')
    dot.edge('kb_embed', 'llm_apis', style='dashed', label='require', fontsize='11', color=GEN_CLUSTER_BORDER, penwidth='1', arrowhead='open')
    dot.edge('kb_summary', 'llm_apis', style='dashed', fontsize='11', color=GEN_CLUSTER_BORDER, penwidth='1', arrowhead='open')

    return dot


def cosmology_architecture():
    """
    Cosmology MCP-KE architecture with simplified 3-color scheme:
    - Blue: HEP-KE products (MCP Client, Analysis-MCP Server, Knowledge-Base-MCP Server)
    - Green: Phase-1 Deliverables (Domain Tools, Agent Tools, Documentation, External Resources)
    - Red: Genesis Infrastructure
    """
    dot = Digraph('Cosmology_Architecture')
    dot.attr(rankdir='LR',
             fontsize='20',
             fontname='Helvetica-Bold',
             labelloc='t',
             label='KE: Agentic Framework Example',
             bgcolor='#FAFAFA',
             pad='0.1',
             nodesep='0.2',
             ranksep='0.3',
             dpi='300')

    # ===========================================
    # COLOR SCHEME
    # ===========================================
    # KE (Blue theme)
    KE_CLUSTER_BG = '#E3F2FD'       # Light blue background
    KE_CLUSTER_BORDER = '#1565C0'   # Dark blue border
    KE_NODE_BG = '#1976D2'          # Blue node
    KE_NODE_BG_LIGHT = '#64B5F6'    # Light blue node
    KE_TEXT = 'white'
    KE_TEXT_DARK = '#0D47A1'

    # Phase-1 Deliverables (Green theme)
    P1_CLUSTER_BG = '#E8F5E9'       # Light green background
    P1_CLUSTER_BORDER = '#2E7D32'   # Dark green border
    P1_NODE_BG = '#43A047'          # Green node
    P1_NODE_BG_LIGHT = '#81C784'    # Light green node
    P1_TEXT = 'white'
    P1_TEXT_DARK = '#1B5E20'

    # Genesis Infrastructure (Red theme)
    GEN_CLUSTER_BG = '#FFEBEE'      # Light red background
    GEN_CLUSTER_BORDER = '#C62828'  # Dark red border
    GEN_NODE_BG = '#EF5350'         # Red node
    GEN_NODE_BG_LIGHT = '#FFCDD2'   # Light red node
    GEN_TEXT = 'white'
    GEN_TEXT_DARK = '#B71C1C'

    # Set default node attributes
    dot.node_attr.update(fontname='Helvetica', fontsize='14')
    dot.edge_attr.update(fontname='Helvetica', fontsize='12')

    # ===========================================
    # LEGEND (Components) - above MCP Client Layer
    # ===========================================
    legend_label = '''<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="4">
        <TR><TD COLSPAN="1"><B>Components</B></TD></TR>
        <TR><TD BGCOLOR="#1976D2"><FONT COLOR="white" POINT-SIZE="12">HEP-KE products</FONT></TD></TR>
        <TR><TD BGCOLOR="#43A047"><FONT COLOR="white" POINT-SIZE="12">Phase-1 deliverables</FONT></TD></TR>
        <TR><TD BGCOLOR="#EF5350"><FONT COLOR="white" POINT-SIZE="12">Genesis Infrastructure</FONT></TD></TR>
    </TABLE>>'''

    # ===========================================
    # KE: MCP Client Layer (Blue) with legend above
    # ===========================================
    with dot.subgraph(name='cluster_left') as left:
        left.attr(label='',
                  style='invis',
                  margin='36')

        # Legend above client
        left.node('legend', legend_label,
                  shape='none',
                  fontsize='14')

        with left.subgraph(name='cluster_client') as c:
            c.attr(label='MCP Client Layer',
                   style='rounded,filled',
                   fillcolor=KE_CLUSTER_BG,
                   color=KE_CLUSTER_BORDER,
                   penwidth='2',
                   fontsize='16',
                   fontname='Helvetica-Bold')
            c.node('client', 'MCP Client\n\n(Any AI system or\napplication)',
                   shape='box',
                   style='rounded,filled',
                   fillcolor=KE_NODE_BG,
                   fontcolor=KE_TEXT,
                   fontsize='14',
                   penwidth='0')

    # ===========================================
    # HEP-KE: Analysis-MCP Server (Blue cluster with green tools inside)
    # ===========================================
    with dot.subgraph(name='cluster_analysis') as s:
        s.attr(label='Analysis-MCP Server',
               style='rounded,filled',
               fillcolor=KE_CLUSTER_BG,
               color=KE_CLUSTER_BORDER,
               penwidth='2',
               fontsize='16',
               fontname='Helvetica-Bold')
        s.node('analysis_server', 'MCP Server\n\nAuto-discovery\nTool execution\nstdio communication',
               shape='box',
               style='rounded,filled',
               fillcolor=KE_NODE_BG,
               fontcolor=KE_TEXT,
               fontsize='14',
               penwidth='0')

        # Domain Tools (Green - Phase-1)
        with s.subgraph(name='cluster_domain') as d:
            d.attr(label='Domain Tools',
                   style='rounded,filled',
                   fillcolor='#C8E6C9',
                   color=P1_CLUSTER_BORDER,
                   penwidth='1.5',
                   fontsize='14',
                   fontname='Helvetica-Bold')
            d.node('power_spectrum', 'Power Spectrum\nComputation',
                   shape='box',
                   style='rounded,filled',
                   fillcolor=P1_NODE_BG_LIGHT,
                   fontcolor=P1_TEXT_DARK,
                   fontsize='13',
                   penwidth='0')
            d.node('model_params', 'Cosmological\nModels',
                   shape='box',
                   style='rounded,filled',
                   fillcolor=P1_NODE_BG_LIGHT,
                   fontcolor=P1_TEXT_DARK,
                   fontsize='13',
                   penwidth='0')
            d.node('data_loading', 'Data Loading\nand Utilities',
                   shape='box',
                   style='rounded,filled',
                   fillcolor=P1_NODE_BG_LIGHT,
                   fontcolor=P1_TEXT_DARK,
                   fontsize='13',
                   penwidth='0')
            d.node('viz_cat', 'Visualization',
                   shape='box',
                   style='rounded,filled',
                   fillcolor=P1_NODE_BG_LIGHT,
                   fontcolor=P1_TEXT_DARK,
                   fontsize='13',
                   penwidth='0')

        # Agent Tools
        with s.subgraph(name='cluster_agent') as a:
            a.attr(label='Agent Tools',
                   style='rounded,filled',
                   fillcolor='#A5D6A7',
                   color=P1_CLUSTER_BORDER,
                   penwidth='1.5',
                   fontsize='14',
                   fontname='Helvetica-Bold')
            a.node('agent1', 'power_spectrum_agent',
                   shape='box',
                   style='rounded,filled',
                   fillcolor=P1_NODE_BG,
                   fontcolor=P1_TEXT,
                   fontsize='13',
                   penwidth='0')
            a.node('agent_more', '...other agents',
                   shape='box',
                   style='rounded,dashed,filled',
                   fillcolor=P1_NODE_BG_LIGHT,
                   fontcolor=P1_TEXT_DARK,
                   fontsize='13',
                   penwidth='1.5',
                   color=P1_CLUSTER_BORDER)

    # ===========================================
    # KE: Knowledge-Base-MCP Server (Blue)
    # ===========================================
    with dot.subgraph(name='cluster_kb') as kb:
        kb.attr(label='Knowledge-Base-MCP Server',
                style='rounded,filled',
                fillcolor=KE_CLUSTER_BG,
                color=KE_CLUSTER_BORDER,
                penwidth='2',
                fontsize='16',
                fontname='Helvetica-Bold')
        kb.node('kb_server', 'MCP Server\n\nDocument retrieval\nSemantic search\nstdio communication',
                shape='box',
                style='rounded,filled',
                fillcolor=KE_NODE_BG,
                fontcolor=KE_TEXT,
                fontsize='14',
                penwidth='0')

        # KB Tools
        with kb.subgraph(name='cluster_kb_tools') as kbt:
            kbt.attr(label='Knowledge Tools',
                     style='rounded,filled',
                     fillcolor='#BBDEFB',
                     color=KE_CLUSTER_BORDER,
                     penwidth='1.5',
                     fontsize='14',
                     fontname='Helvetica-Bold')
            kbt.node('kb_embed', 'Embeddings',
                     shape='box',
                     style='rounded,filled',
                     fillcolor=KE_NODE_BG_LIGHT,
                     fontcolor=KE_TEXT_DARK,
                     fontsize='13',
                     penwidth='0')
            kbt.node('kb_docs', 'Documentation',
                     shape='box',
                     style='rounded,filled',
                     fillcolor=P1_NODE_BG_LIGHT,
                     fontcolor=P1_TEXT_DARK,
                     fontsize='13',
                     penwidth='0')
            kbt.node('kb_summary', 'Summarization',
                     shape='box',
                     style='rounded,filled',
                     fillcolor=KE_NODE_BG_LIGHT,
                     fontcolor=KE_TEXT_DARK,
                     fontsize='13',
                     penwidth='0')

    # ===========================================
    # PHASE-1: Cosmology Resources (Green)
    # ===========================================
    with dot.subgraph(name='cluster_cosmo_data') as md:
        md.attr(label='Cosmology\nResources',
                style='dashed,rounded',
                color=P1_CLUSTER_BORDER,
                fillcolor=P1_CLUSTER_BG,
                penwidth='1.5',
                fontsize='14',
                fontname='Helvetica')
        md.node('class_code', 'CLASS\nCosmology Code',
                shape='ellipse',
                style='filled',
                fillcolor=P1_NODE_BG_LIGHT,
                fontcolor=P1_TEXT_DARK,
                fontsize='13',
                penwidth='0')
        md.node('obs_data', 'eBOSS\nObservational Data',
                shape='ellipse',
                style='filled',
                fillcolor=P1_NODE_BG_LIGHT,
                fontcolor=P1_TEXT_DARK,
                fontsize='13',
                penwidth='0')

    # ===========================================
    # GENESIS: Infrastructure (Red)
    # ===========================================
    with dot.subgraph(name='cluster_genesis') as g:
        g.attr(label='Genesis Infrastructure',
               style='dashed,rounded',
               color=GEN_CLUSTER_BORDER,
               fillcolor=GEN_CLUSTER_BG,
               penwidth='1.5',
               fontsize='14',
               fontname='Helvetica')
        g.node('llm_apis', 'AmSC LLM APIs',
               shape='ellipse',
               style='filled',
               fillcolor=GEN_NODE_BG_LIGHT,
               fontcolor=GEN_TEXT_DARK,
               fontsize='13',
               penwidth='0')
        g.node('data_apis', 'Data APIs',
               shape='ellipse',
               style='filled',
               fillcolor=GEN_NODE_BG_LIGHT,
               fontcolor=GEN_TEXT_DARK,
               fontsize='13',
               penwidth='0')

    # ===========================================
    # EDGES
    # ===========================================
    # Main connections - Client to servers
    dot.edge('client', 'analysis_server',
             label='MCP\nProtocol',
             fontsize='12',
             color=KE_CLUSTER_BORDER,
             penwidth='3',
             arrowhead='vee')
    dot.edge('client', 'kb_server',
             label='MCP\nProtocol',
             fontsize='12',
             color=KE_CLUSTER_BORDER,
             penwidth='3',
             arrowhead='vee')

    # Analysis server to tools (green edges for Phase-1 tools)
    dot.edge('analysis_server', 'power_spectrum', color=P1_CLUSTER_BORDER, penwidth='2', arrowhead='vee')
    dot.edge('analysis_server', 'model_params', color=P1_CLUSTER_BORDER, penwidth='2', arrowhead='vee')
    dot.edge('analysis_server', 'data_loading', color=P1_CLUSTER_BORDER, penwidth='2', arrowhead='vee')
    dot.edge('analysis_server', 'viz_cat', color=P1_CLUSTER_BORDER, penwidth='2', arrowhead='vee')
    dot.edge('analysis_server', 'agent1', color=P1_CLUSTER_BORDER, penwidth='2', arrowhead='vee')
    dot.edge('analysis_server', 'agent_more', style='dashed', color=P1_CLUSTER_BORDER, penwidth='1.5', arrowhead='vee')

    # KB server to tools
    dot.edge('kb_server', 'kb_embed', color=KE_CLUSTER_BORDER, penwidth='2', arrowhead='vee')
    dot.edge('kb_server', 'kb_docs', color=KE_CLUSTER_BORDER, penwidth='2', arrowhead='vee')
    dot.edge('kb_server', 'kb_summary', color=KE_CLUSTER_BORDER, penwidth='2', arrowhead='vee')

    # Cosmology data dependencies (Phase-1 color)
    dot.edge('model_params', 'class_code', style='dashed', fontsize='11', color=P1_CLUSTER_BORDER, penwidth='1', arrowhead='open')
    dot.edge('data_loading', 'obs_data', style='dashed', fontsize='11', color=P1_CLUSTER_BORDER, penwidth='1', arrowhead='open')

    # Genesis infrastructure dependencies (Red color)
    dot.edge('agent1', 'llm_apis', style='dashed', label='require', fontsize='11', color=GEN_CLUSTER_BORDER, penwidth='1', arrowhead='open')
    dot.edge('kb_embed', 'llm_apis', style='dashed', label='require', fontsize='11', color=GEN_CLUSTER_BORDER, penwidth='1', arrowhead='open')
    dot.edge('kb_summary', 'llm_apis', style='dashed', fontsize='11', color=GEN_CLUSTER_BORDER, penwidth='1', arrowhead='open')

    return dot


if __name__ == '__main__':
    print("Generating flowcharts...")

    d_generic = generic_architecture()
    d_generic.render('generic_architecture', format='png', cleanup=True)
    print("Generated generic_architecture.png")

    d_mu2e = mu2e_architecture()
    d_mu2e.render('mu2e_architecture', format='png', cleanup=True)
    print("Generated mu2e_architecture.png")

    d_cosmo = cosmology_architecture()
    d_cosmo.render('cosmology_architecture', format='png', cleanup=True)
    print("Generated cosmology_architecture.png")

    print("\nAll flowcharts generated successfully!")
