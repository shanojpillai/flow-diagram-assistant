"""
Diagram Generator - Module for generating flow diagrams
"""
import io
import base64
from typing import Dict, Any, List, Optional, Union
import logging
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path
import plotly.graph_objects as go

class DiagramGenerator:
    """Generator for flow diagrams from structured data"""
    
    def __init__(self):
        """Initialize DiagramGenerator"""
        self.logger = logging.getLogger(__name__)
        
        # Node type styling
        self.node_styles = {
            "process": {"shape": "box", "color": "#4285F4", "fontcolor": "white"},
            "decision": {"shape": "diamond", "color": "#FBBC05", "fontcolor": "black"},
            "start": {"shape": "oval", "color": "#34A853", "fontcolor": "white"},
            "end": {"shape": "oval", "color": "#EA4335", "fontcolor": "white"},
            "io": {"shape": "parallelogram", "color": "#9C27B0", "fontcolor": "white"},
            "default": {"shape": "box", "color": "#4285F4", "fontcolor": "white"}
        }
        
        # Edge type styling
        self.edge_styles = {
            "normal": {"style": "solid", "color": "#333333", "width": 1.5},
            "conditional": {"style": "dashed", "color": "#FF9800", "width": 1.5},
            "feedback": {"style": "dotted", "color": "#9C27B0", "width": 1.5},
            "default": {"style": "solid", "color": "#333333", "width": 1.5}
        }
    
    def generate(self, diagram_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a flow diagram from structured data
        
        Args:
            diagram_data: Structured data defining the flow diagram
            
        Returns:
            Dict[str, Any]: Enriched diagram data with layout information
        """
        self.logger.info("Generating flow diagram")
        
        # Validate diagram data
        self._validate_diagram_data(diagram_data)
        
        # Create a directed graph
        G = nx.DiGraph()
        
        # Add nodes with attributes
        for node in diagram_data["nodes"]:
            node_style = self.node_styles.get(node.get("type", "default"), self.node_styles["default"])
            G.add_node(
                node["id"],
                label=node["label"],
                node_type=node.get("type", "process"),
                description=node.get("description", ""),
                **node_style
            )
        
        # Add edges with attributes
        for edge in diagram_data["edges"]:
            edge_style = self.edge_styles.get(edge.get("type", "default"), self.edge_styles["default"])
            G.add_edge(
                edge["from"],
                edge["to"],
                label=edge.get("label", ""),
                edge_type=edge.get("type", "normal"),
                **edge_style
            )
        
        # Calculate layout
        layout = self._calculate_layout(G)
        
        # Add layout to diagram data
        enriched_data = diagram_data.copy()
        enriched_data["layout"] = layout
        enriched_data["graph"] = G
        
        return enriched_data
    
    def _validate_diagram_data(self, diagram_data: Dict[str, Any]) -> None:
        """
        Validate diagram data structure
        
        Args:
            diagram_data: Diagram data to validate
            
        Raises:
            ValueError: If diagram data is invalid
        """
        # Check required keys
        required_keys = ["nodes", "edges", "title"]
        for key in required_keys:
            if key not in diagram_data:
                raise ValueError(f"Missing required key in diagram data: {key}")
        
        # Check nodes have required fields
        for i, node in enumerate(diagram_data["nodes"]):
            if "id" not in node:
                raise ValueError(f"Node at index {i} is missing 'id' field")
            if "label" not in node:
                raise ValueError(f"Node with id '{node.get('id', i)}' is missing 'label' field")
        
        # Check edges have required fields
        for i, edge in enumerate(diagram_data["edges"]):
            if "from" not in edge:
                raise ValueError(f"Edge at index {i} is missing 'from' field")
            if "to" not in edge:
                raise ValueError(f"Edge at index {i} is missing 'to' field")
            
            # Check nodes referenced by edges exist
            node_ids = [node["id"] for node in diagram_data["nodes"]]
            if edge["from"] not in node_ids:
                raise ValueError(f"Edge references non-existent node id: {edge['from']}")
            if edge["to"] not in node_ids:
                raise ValueError(f"Edge references non-existent node id: {edge['to']}")
    
    def _calculate_layout(self, G: nx.DiGraph) -> Dict[str, List[float]]:
        """
        Calculate layout positions for nodes
        
        Args:
            G: NetworkX graph
            
        Returns:
            Dict[str, List[float]]: Node positions {node_id: [x, y]}
        """
        # Use hierarchical layout for flow diagrams
        try:
            # Try using sugiyama layout for better flow diagrams
            pos = nx.multipartite_layout(G, subset_key="node_type")
        except:
            # Fall back to dot layout if sugiyama fails
            pos = nx.nx_pydot.graphviz_layout(G, prog="dot")
        
        # If both fail, use a simple layout
        if not pos:
            pos = nx.spring_layout(G)
        
        return {node: pos[node].tolist() for node in G.nodes()}
    
    def display(self, diagram_data: Dict[str, Any]) -> None:
        """
        Display the diagram in Streamlit
        
        Args:
            diagram_data: Enriched diagram data with layout information
        """
        G = diagram_data["graph"]
        pos = {node: diagram_data["layout"][node] for node in G.nodes()}
        
        # Create figure using Plotly for interactivity
        fig = go.Figure()
        
        # Add edges
        for edge in G.edges():
            from_node, to_node = edge
            x0, y0 = pos[from_node]
            x1, y1 = pos[to_node]
            
            edge_data = G.edges[edge]
            
            # Create edge line
            fig.add_trace(go.Scatter(
                x=[x0, x1],
                y=[y0, y1],
                mode='lines',
                line=dict(
                    color=edge_data.get("color", "#333"),
                    width=edge_data.get("width", 1.5),
                    dash='solid' if edge_data.get("style", "solid") == "solid" else 'dash'
                ),
                hoverinfo='text',
                text=edge_data.get("label", ""),
                name=f"Edge: {edge_data.get('label', f'{from_node} to {to_node}')}",
                showlegend=False
            ))
            
            # Add arrow marker at midpoint
            mid_x = (x0 + x1) / 2
            mid_y = (y0 + y1) / 2
            angle = np.arctan2(y1 - y0, x1 - x0) * 180 / np.pi
            
            # Add text label for the edge if it exists
            if "label" in edge_data and edge_data["label"]:
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
        
        # Add nodes
        for node in G.nodes():
            x, y = pos[node]
            node_data = G.nodes[node]
            node_type = node_data.get("node_type", "process")
            color = node_data.get("color", "#4285F4")
            
            # Create different shapes based on node type
            if node_type == "decision":
                marker_symbol = "diamond"
                marker_size = 15
            elif node_type in ["start", "end"]:
                marker_symbol = "circle"
                marker_size = 12
            else:
                marker_symbol = "square"
                marker_size = 14
            
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
                name=f"Node: {node_data.get('label', node)}",
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
        
        # Display in Streamlit
        st.plotly_chart(fig, use_container_width=True)
    
    def export_as_png(self, diagram_data: Dict[str, Any]) -> bytes:
        """
        Export diagram as PNG
        
        Args:
            diagram_data: Enriched diagram data
            
        Returns:
            bytes: PNG image data
        """
        # Create a matplotlib figure
        fig, ax = plt.subplots(figsize=(10, 8))
        
        G = diagram_data["graph"]
        pos = {node: diagram_data["layout"][node] for node in G.nodes()}
        
        # Draw edges
        for edge in G.edges():
            from_node, to_node = edge
            edge_data = G.edges[edge]
            edge_style = "-" if edge_data.get("style", "solid") == "solid" else "--"
            
            nx.draw_networkx_edges(
                G, pos,
                edgelist=[edge],
                width=edge_data.get("width", 1.5),
                edge_color=edge_data.get("color", "#333333"),
                style=edge_style,
                ax=ax
            )
            
            # Add edge labels if they exist
            if "label" in edge_data and edge_data["label"]:
                edge_labels = {edge: edge_data["label"]}
                nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, ax=ax)
        
        # Draw nodes
        for node_type in set(nx.get_node_attributes(G, "node_type").values()):
            node_list = [n for n, d in G.nodes(data=True) if d.get("node_type") == node_type]
            
            if node_list:
                node_shape = self.node_styles.get(node_type, self.node_styles["default"])["shape"]
                node_color = [G.nodes[n].get("color", "#4285F4") for n in node_list]
                
                nx.draw_networkx_nodes(
                    G, pos,
                    nodelist=node_list,
                    node_color=node_color,
                    node_shape=node_shape if node_shape != "diamond" else "d",
                    node_size=700,
                    ax=ax
                )
        
        # Draw node labels
        node_labels = {n: G.nodes[n].get("label", n) for n in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10, font_color="black", ax=ax)
        
        # Set title
        plt.title(diagram_data.get("title", "Flow Diagram"))
        
        # Turn off axis
        plt.axis("off")
        
        # Save to bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=150, bbox_inches="tight", transparent=False)
        plt.close(fig)
        buf.seek(0)
        
        return buf.getvalue()
    
    def export_as_svg(self, diagram_data: Dict[str, Any]) -> str:
        """
        Export diagram as SVG
        
        Args:
            diagram_data: Enriched diagram data
            
        Returns:
            str: SVG content as string
        """
        # Create a matplotlib figure
        fig, ax = plt.subplots(figsize=(10, 8))
        
        G = diagram_data["graph"]
        pos = {node: diagram_data["layout"][node] for node in G.nodes()}
        
        # Draw the graph similar to export_as_png
        # (Same drawing code as in export_as_png)
        # Draw edges
        for edge in G.edges():
            from_node, to_node = edge
            edge_data = G.edges[edge]
            edge_style = "-" if edge_data.get("style", "solid") == "solid" else "--"
            
            nx.draw_networkx_edges(
                G, pos,
                edgelist=[edge],
                width=edge_data.get("width", 1.5),
                edge_color=edge_data.get("color", "#333333"),
                style=edge_style,
                ax=ax
            )
            
            # Add edge labels if they exist
            if "label" in edge_data and edge_data["label"]:
                edge_labels = {edge: edge_data["label"]}
                nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, ax=ax)
        
        # Draw nodes
        for node_type in set(nx.get_node_attributes(G, "node_type").values()):
            node_list = [n for n, d in G.nodes(data=True) if d.get("node_type") == node_type]
            
            if node_list:
                node_shape = self.node_styles.get(node_type, self.node_styles["default"])["shape"]
                node_color = [G.nodes[n].get("color", "#4285F4") for n in node_list]
                
                nx.draw_networkx_nodes(
                    G, pos,
                    nodelist=node_list,
                    node_color=node_color,
                    node_shape=node_shape if node_shape != "diamond" else "d",
                    node_size=700,
                    ax=ax
                )
        
        # Draw node labels
        node_labels = {n: G.nodes[n].get("label", n) for n in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=10, font_color="black", ax=ax)
        
        # Set title
        plt.title(diagram_data.get("title", "Flow Diagram"))
        
        # Turn off axis
        plt.axis("off")
        
        # Save to SVG string
        buf = io.StringIO()
        plt.savefig(buf, format="svg", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        
        return buf.getvalue()