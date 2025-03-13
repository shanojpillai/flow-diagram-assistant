"""
Mermaid Diagram Generator - Module for generating Mermaid diagrams
"""
import streamlit as st
from typing import Dict, Any, Optional

def generate_mermaid(diagram_data: Dict[str, Any]) -> str:
    """
    Generate Mermaid diagram code from structured data
    
    Args:
        diagram_data: Structured diagram data
        
    Returns:
        str: Mermaid diagram code
    """
    # Start with flowchart definition
    mermaid_code = ["flowchart TD"]
    
    # Track processed nodes for styling
    node_ids = []
    
    # Add nodes with styling
    for node in diagram_data.get("nodes", []):
        node_id = node.get("id", "")
        if not node_id:
            continue
            
        node_ids.append(node_id)
        node_label = node.get("label", node_id)
        node_type = node.get("type", "process")
        
        # Determine node styling based on type
        if node_type == "start":
            mermaid_code.append(f'    {node_id}(["{node_label}"])')
            mermaid_code.append(f'    style {node_id} fill:#34A853,stroke:#333,color:white')
        elif node_type == "end":
            mermaid_code.append(f'    {node_id}(["{node_label}"])')
            mermaid_code.append(f'    style {node_id} fill:#EA4335,stroke:#333,color:white')
        elif node_type == "decision":
            mermaid_code.append(f'    {node_id}{{{"{node_label}"}}}')
            mermaid_code.append(f'    style {node_id} fill:#FBBC05,stroke:#333,color:black')
        elif node_type == "io":
            mermaid_code.append(f'    {node_id}[/"{node_label}"/]')
            mermaid_code.append(f'    style {node_id} fill:#9C27B0,stroke:#333,color:white')
        else:  # process or default
            mermaid_code.append(f'    {node_id}["{node_label}"]')
            mermaid_code.append(f'    style {node_id} fill:#4285F4,stroke:#333,color:white')
    
    # Add edges
    for edge in diagram_data.get("edges", []):
        from_node = edge.get("from", "")
        to_node = edge.get("to", "")
        if not from_node or not to_node:
            continue
            
        edge_label = edge.get("label", "")
        edge_type = edge.get("type", "normal")
        
        # Determine edge styling based on type
        if edge_type == "conditional":
            link_style = " -- "
            if edge_label:
                link_style = f" -- {edge_label} -- "
            mermaid_code.append(f'    {from_node}{link_style}>{to_node}')
            mermaid_code.append(f'    linkStyle {len(mermaid_code) - 2 - len(node_ids)} stroke:#FF9800,stroke-width:2px,stroke-dasharray: 5 5')
        elif edge_type == "feedback":
            link_style = " -.- "
            if edge_label:
                link_style = f" -.- {edge_label} -.- "
            mermaid_code.append(f'    {from_node}{link_style}>{to_node}')
            mermaid_code.append(f'    linkStyle {len(mermaid_code) - 2 - len(node_ids)} stroke:#9C27B0,stroke-width:2px')
        else:  # normal or default
            link_style = " --- "
            if edge_label:
                link_style = f" --- {edge_label} --- "
            mermaid_code.append(f'    {from_node}{link_style}>{to_node}')
    
    # Add title as a comment
    title = diagram_data.get("title", "Flow Diagram")
    mermaid_code.insert(1, f"    %% {title}")
    
    return "\n".join(mermaid_code)

def display_mermaid(diagram_data: Dict[str, Any], container: Optional[st.container] = None) -> None:
    """
    Display a Mermaid diagram in Streamlit
    
    Args:
        diagram_data: Structured diagram data
        container: Optional Streamlit container to display in
    """
    if container is None:
        container = st
        
    mermaid_code = generate_mermaid(diagram_data)
    
    # Display the diagram
    container.markdown(f"### {diagram_data.get('title', 'Flow Diagram')}")
    container.markdown(f"```mermaid\n{mermaid_code}\n```")
    
    # Also provide the code for copying
    with container.expander("Mermaid Code"):
        container.code(mermaid_code, language="mermaid")

def export_mermaid(diagram_data: Dict[str, Any]) -> str:
    """
    Export diagram as Mermaid code
    
    Args:
        diagram_data: Structured diagram data
        
    Returns:
        str: Mermaid diagram code
    """
    return generate_mermaid(diagram_data)