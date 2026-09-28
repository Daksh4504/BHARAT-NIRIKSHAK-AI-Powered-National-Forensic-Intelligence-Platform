"""
Plotly-based Interactive Network Graph Visualizer for Entity Linking.
Visualizes links between Current FIR, Historical FIRs, Accused Persons,
Vehicles, Phone Numbers, and MO Signatures.
"""

from typing import Dict, Any
import networkx as nx
import plotly.graph_objects as go


def generate_network_graph_figure(G: nx.Graph) -> go.Figure:
    """Generate an interactive Plotly network diagram from a NetworkX graph."""
    if len(G.nodes) == 0:
        fig = go.Figure()
        fig.update_layout(title="No entities to display in network graph.")
        return fig

    # Layout algorithm
    pos = nx.spring_layout(G, k=0.7, iterations=50, seed=42)

    # Node styling config
    type_color_map = {
        "Case": "#3B82F6",         # Blue
        "Suspect": "#EF4444",      # Red
        "Vehicle": "#F59E0B",      # Amber
        "Phone": "#8B5CF6",        # Purple
        "MO_Signature": "#10B981", # Emerald
        "Tool_Weapon": "#EC4899"   # Pink
    }
    
    # Edge traces
    edge_x = []
    edge_y = []
    edge_hover_text = []

    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=1.5, color='#94A3B8'),
        hoverinfo='none',
        mode='lines'
    )

    # Node traces
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    node_size = []
    node_symbols = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        node_data = G.nodes[node]
        n_type = node_data.get("node_type", "Other")
        n_label = node_data.get("label", node)
        is_cur = node_data.get("is_current", False)

        color = "#1D4ED8" if is_cur else type_color_map.get(n_type, "#64748B")
        size = 28 if (is_cur or n_type == "Suspect") else 20
        symbol = "star" if is_cur else "circle"

        node_color.append(color)
        node_size.append(size)
        node_symbols.append(symbol)

        hover_info = f"<b>{n_label}</b><br>Type: {n_type}"
        if "crime_type" in node_data:
            hover_info += f"<br>Crime: {node_data['crime_type']}"
        if is_cur:
            hover_info += "<br><span style='color:yellow;'>★ CURRENT INVESTIGATION CASE</span>"
        node_text.append(hover_info)

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        hoverinfo='text',
        hovertext=node_text,
        text=[G.nodes[node].get("label", "")[:18] for node in G.nodes()],
        textposition="bottom center",
        textfont=dict(size=10, color="#CBD5E1"),
        marker=dict(
            showscale=False,
            color=node_color,
            size=node_size,
            symbol=node_symbols,
            line_width=2,
            line_color='#FFFFFF'
        )
    )

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title=dict(
                text="Entity & Modus Operandi Linkage Graph (Cross-Case Corroboration)",
                font=dict(size=15, color="#F8FAFC")
            ),
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=10, r=10, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='rgba(15, 23, 42, 0.95)',
            paper_bgcolor='rgba(15, 23, 42, 0.95)',
            height=480
        )
    )

    return fig
