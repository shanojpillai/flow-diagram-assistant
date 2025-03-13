"""
GIF export module for Flow Diagram Animation Assistant
"""
import io
import tempfile
import os
from typing import Dict, Any, List, Optional, Union
import logging
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PIL import Image, ImageDraw, ImageFont
import networkx as nx

# Get logger
logger = logging.getLogger(__name__)

def export_as_gif(diagram_data: Dict[str, Any], duration: float = 3.0, fps: int = 20) -> bytes:
    """
    Export diagram animation as GIF
    
    Args:
        diagram_data: Enriched diagram data with layout information
        duration: Total duration of the animation in seconds
        fps: Frames per second for the GIF
        
    Returns:
        bytes: GIF image data
    """
    logger.info("Exporting diagram animation as GIF")
    
    G = diagram_data["graph"]
    pos = {node: diagram_data["layout"][node] for node in G.nodes()}
    
    # Get animation sequence
    animations = diagram_data.get("animations", [])
    
    # If no animations defined, create a default sequence
    if not animations:
        animations = _create_default_animations(diagram_data)
    
    # Sort animations by order
    animations.sort(key=lambda x: x.get("order", 0))
    
    # Calculate total frames based on duration and fps
    total_frames = int(duration * fps)
    
    # Create a figure for the animation
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Initialize sets to track visibility
    visible_nodes = set()
    visible_edges = set()
    highlighted_nodes = set()
    highlighted_edges = set()
    
    # Calculate frame mapping for animations
    max_order = max([anim.get("order", 0) for anim in animations])
    frames_per_step = total_frames / max_order if max_order > 0 else total_frames
    
    # Function to draw the current state at a given frame
    def draw_frame(frame_num):
        # Clear the axes for the new frame
        ax.clear()
        
        # Calculate current animation step
        current_step = int(frame_num / frames_per_step) + 1
        
        # Update visibility based on animations up to current step
        for anim in animations:
            order = anim.get("order", 0)
            if order <= current_step:
                element = anim.get("element", "")
                effect = anim.get("effect", "")
                
                # Handle node animations
                if element in G.nodes():
                    if effect in ["fadeIn", "highlight", "pulse"]:
                        visible_nodes.add(element)
                    
                    if effect == "highlight":
                        highlighted_nodes.add(element)
                
                # Handle edge animations
                elif element.startswith("edge_"):
                    parts = element.split("_")[1:]
                    if len(parts) >= 2:
                        from_node, to_node = parts[0], parts[1]
                        edge = (from_node, to_node)
                        
                        if edge in G.edges() or (to_node, from_node) in G.edges():
                            if effect in ["draw", "fadeIn", "highlight"]:
                                visible_edges.add(edge)
                            
                            if effect == "highlight":
                                highlighted_edges.add(edge)
        
        # Draw edges
        for edge in G.edges():
            if edge not in visible_edges:
                continue
                
            edge_data = G.edges[edge]
            edge_style = "--" if edge_data.get("style", "solid") == "dashed" else "-"
            edge_width = edge_data.get("width", 1.5)
            
            # Highlight edges that are in the highlighted set
            if edge in highlighted_edges:
                edge_color = "#FF9800"  # Orange for highlighting
                edge_width *= 1.5
            else:
                edge_color = edge_data.get("color", "#333333")
            
            # Draw the edge
            from_node, to_node = edge
            nx.draw_networkx_edges(
                G, pos,
                edgelist=[edge],
                width=edge_width,
                edge_color=edge_color,
                style=edge_style,
                arrows=True,
                arrowsize=15,
                ax=ax
            )
            
            # Add edge labels if they exist
            if "label" in edge_data and edge_data["label"]:
                label_pos = {edge: (
                    (pos[from_node][0] + pos[to_node][0]) / 2,
                    (pos[from_node][1] + pos[to_node][1]) / 2
                )}
                nx.draw_networkx_edge_labels(
                    G, pos,
                    edge_labels={edge: edge_data["label"]},
                    font_size=8,
                    bbox=dict(facecolor="white", edgecolor="none", alpha=0.7),
                    ax=ax
                )
        
        # Draw nodes
        for node_type in set(nx.get_node_attributes(G, "node_type").values()):
            # Filter nodes by type and visibility
            node_list = [
                n for n, d in G.nodes(data=True) 
                if d.get("node_type") == node_type and n in visible_nodes
            ]
            
            if not node_list:
                continue
            
            # Get colors for each node
            node_colors = []
            for node in node_list:
                if node in highlighted_nodes:
                    node_colors.append("#FF9800")  # Orange for highlighting
                else:
                    node_colors.append(G.nodes[node].get("color", "#4285F4"))
            
            # Determine node shape based on type
            if node_type == "decision":
                node_shape = "d"  # Diamond
            elif node_type in ["start", "end"]:
                node_shape = "o"  # Circle
            else:
                node_shape = "s"  # Square
            
            # Draw the nodes
            nx.draw_networkx_nodes(
                G, pos,
                nodelist=node_list,
                node_color=node_colors,
                node_shape=node_shape,
                node_size=700,
                ax=ax
            )
        
        # Draw node labels for visible nodes
        label_nodes = {n: G.nodes[n].get("label", n) for n in visible_nodes}
        if label_nodes:
            nx.draw_networkx_labels(
                G, pos,
                labels=label_nodes,
                font_size=10,
                font_color="black",
                ax=ax
            )
        
        # Set title
        ax.set_title(diagram_data.get("title", "Flow Diagram"))
        
        # Turn off axis
        ax.axis("off")
        
        return ax
    
    # Create animation
    ani = animation.FuncAnimation(
        fig, draw_frame, frames=total_frames, interval=1000/fps, blit=False
    )
    
    # Save to bytes buffer
    with tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as temp_file:
        # Save animation to temporary file
        ani.save(
            temp_file.name, 
            writer='pillow', 
            fps=fps, 
            dpi=100
        )
        plt.close(fig)
        
        # Read the file back as bytes
        with open(temp_file.name, 'rb') as f:
            gif_data = f.read()
    
    # Clean up the temporary file
    os.unlink(temp_file.name)
    
    return gif_data

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