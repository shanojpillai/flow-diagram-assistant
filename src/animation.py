"""
Animation Module - Functions for animating flow diagrams
"""
import time
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from typing import Dict, Any, List, Optional, Union
import uuid
import networkx as nx

def animate_diagram(diagram_data: Dict[str, Any], speed: float = 1.0, container: Optional[st.container] = None) -> None:
    """
    Animate a flow diagram
    
    Args:
        diagram_data: Enriched diagram data with layout information
        speed: Animation speed multiplier (lower is slower)
        container: Streamlit container to render the animation in
    """
    # Get the display container
    if container is None:
        container = st
    
    # Get the graph and layout
    G = diagram_data["graph"]
    pos = {node: diagram_data["layout"][node] for node in G.nodes()}
    
    # Get animation sequence
    animations = diagram_data.get("animations", [])
    
    # If no animations defined, create a default sequence
    if not animations:
        animations = _create_default_animations(diagram_data)
    
    # Sort animations by order
    animations.sort(key=lambda x: x.get("order", 0))
    
    # Create a placeholder for the figure
    fig_placeholder = container.empty()
    
    # Execute animations
    visible_nodes = set()
    visible_edges = set()
    highlighted_nodes = set()
    highlighted_edges = set()
    pulsing_nodes = set()
    
    # Group animations by order for simultaneous effects
    animation_groups = {}
    for anim in animations:
        order = anim.get("order", 0)
        if order not in animation_groups:
            animation_groups[order] = []
        animation_groups[order].append(anim)
    
    # Process animation groups in order
    for order in sorted(animation_groups.keys()):
        group = animation_groups[order]
        
        # Generate a unique key for this animation frame
        frame_key = f"animation_frame_{order}_{uuid.uuid4().hex[:8]}"
        
        # Apply all animations in the group
        for anim in group:
            element = anim.get("element", "")
            effect = anim.get("effect", "")
            
            # Handle node animations
            if element in G.nodes():
                if effect == "fadeIn":
                    visible_nodes.add(element)
                elif effect == "highlight":
                    visible_nodes.add(element)
                    highlighted_nodes.add(element)
                elif effect == "pulse":
                    visible_nodes.add(element)
                    pulsing_nodes.add(element)
            
            # Handle edge animations
            elif element.startswith("edge_"):
                parts = element.split("_")[1:]
                if len(parts) >= 2:
                    from_node, to_node = parts[0], parts[1]
                    edge = (from_node, to_node)
                    
                    if edge in G.edges() or (to_node, from_node) in G.edges():
                        if effect == "draw" or effect == "fadeIn":
                            visible_edges.add(edge)
                        elif effect == "highlight":
                            visible_edges.add(edge)
                            highlighted_edges.add(edge)
        
        # Render the current state
        fig = _create_animated_figure(
            diagram_data, 
            visible_nodes, 
            visible_edges, 
            highlighted_nodes, 
            highlighted_edges,
            pulsing_nodes
        )
        fig_placeholder.plotly_chart(fig, use_container_width=True, key=frame_key)
        
        # Wait based on animation duration and speed
        duration = max([anim.get("duration", 0.8) for anim in group])
        time.sleep(duration / speed)
    
    # Final render with everything visible - use a unique key
    final_key = f"animation_final_{uuid.uuid4().hex[:8]}"
    visible_nodes = set(G.nodes())
    visible_edges = set(G.edges())
    highlighted_nodes = set()
    highlighted_edges = set()
    pulsing_nodes = set()
    
    fig = _create_animated_figure(
        diagram_data, 
        visible_nodes, 
        visible_edges, 
        highlighted_nodes, 
        highlighted_edges,
        pulsing_nodes
    )
    fig_placeholder.plotly_chart(fig, use_container_width=True, key=final_key)

def _create_default_animations(diagram_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Create default animations for a diagram
    
    Args:
        diagram_data: Diagram data
        
    Returns:
        List[Dict[str, Any]]: List of animation instructions
    """
    animations = []
    G = diagram_data["graph"]
    
    # Get topological ordering of nodes if possible
    try:
        node_order = list(nx.topological_sort(G))
    except:
        # Fall back to original order if graph has cycles
        node_order = list(G.nodes())
    
    # Create node appearance animations
    for i, node in enumerate(node_order):
        animations.append({
            "element": node,
            "effect": "fadeIn",
            "duration": 0.5,
            "order": i + 1
        })
    
    # Create edge appearance animations
    edge_i = 0
    for i, node in enumerate(node_order[:-1]):
        for successor in G.successors(node):
            edge_i += 1
            animations.append({
                "element": f"edge_{node}_{successor}",
                "effect": "draw",
                "duration": 0.3,
                "order": len(node_order) + edge_i
            })
    
    return animations

def _create_animated_figure(
    diagram_data: Dict[str, Any],
    visible_nodes: set,
    visible_edges: set,
    highlighted_nodes: set,
    highlighted_edges: set,
    pulsing_nodes: set
) -> go.Figure:
    """
    Create a Plotly figure for the current animation state
    
    Args:
        diagram_data: Enriched diagram data
        visible_nodes: Set of currently visible nodes
        visible_edges: Set of currently visible edges
        highlighted_nodes: Set of highlighted nodes
        highlighted_edges: Set of highlighted edges
        pulsing_nodes: Set of pulsing nodes
        
    Returns:
        go.Figure: Plotly figure
    """
    G = diagram_data["graph"]
    pos = {node: diagram_data["layout"][node] for node in G.nodes()}
    
    # Create figure
    fig = go.Figure()
    
    # Add visible edges
    for edge in G.edges():
        if edge not in visible_edges:
            continue
            
        from_node, to_node = edge
        x0, y0 = pos[from_node]
        x1, y1 = pos[to_node]
        
        edge_data = G.edges[edge]
        
        # Determine if edge is highlighted
        is_highlighted = edge in highlighted_edges
        
        # Create edge line with appropriate styling
        line_color = "#FF9800" if is_highlighted else edge_data.get("color", "#333")
        line_width = edge_data.get("width", 1.5) * (2 if is_highlighted else 1)
        
        fig.add_trace(go.Scatter(
            x=[x0, x1],
            y=[y0, y1],
            mode='lines',
            line=dict(
                color=line_color,
                width=line_width,
                dash='solid' if edge_data.get("style", "solid") == "solid" else 'dash'
            ),
            hoverinfo='text',
            text=edge_data.get("label", ""),
            showlegend=False
        ))
        
        # Add edge label if it exists
        if "label" in edge_data and edge_data["label"]:
            mid_x = (x0 + x1) / 2
            mid_y = (y0 + y1) / 2
            
            fig.add_annotation(
                x=mid_x,
                y=mid_y,
                text=edge_data["label"],
                showarrow=False,
                font=dict(size=10),
                bgcolor="rgba(255, 255, 255, 0.8)",
                bordercolor="#333",
                borderwidth=1
            )
    
    # Add visible nodes
    for node in G.nodes():
        if node not in visible_nodes:
            continue
            
        x, y = pos[node]
        node_data = G.nodes[node]
        node_type = node_data.get("node_type", "process")
        
        # Determine if node is highlighted or pulsing
        is_highlighted = node in highlighted_nodes
        is_pulsing = node in pulsing_nodes
        
        # Adjust color and size based on highlight/pulse state
        base_color = node_data.get("color", "#4285F4")
        color = "#FF9800" if is_highlighted else base_color
        size_multiplier = 1.5 if is_highlighted or is_pulsing else 1.0
        
        # Create different shapes based on node type
        if node_type == "decision":
            marker_symbol = "diamond"
            marker_size = 15 * size_multiplier
        elif node_type in ["start", "end"]:
            marker_symbol = "circle"
            marker_size = 12 * size_multiplier
        else:
            marker_symbol = "square"
            marker_size = 14 * size_multiplier
        
        fig.add_trace(go.Scatter(
            x=[x],
            y=[y],
            mode='markers+text',
            marker=dict(
                symbol=marker_symbol,
                size=marker_size,
                color=color,
                line=dict(width=1, color='#333')
            ),
            text=node_data.get("label", node),
            textposition="middle center",
            hoverinfo='text',
            hovertext=node_data.get("description", ""),
            showlegend=False
        ))
    
    # Configure layout
    fig.update_layout(
        title=diagram_data.get("title", "Flow Diagram"),
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='white'
    )
    
    return fig