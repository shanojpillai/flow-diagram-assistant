"""
System design templates
"""
import streamlit as st

def display_system_design_template(container=None):
    """
    Display a predefined system design template
    """
    if container is None:
        container = st
        
    mermaid_code = """flowchart TD
    user([User/Client])
    lb[Load Balancer]
    web1[Web Server 1]
    web2[Web Server 2]
    api[API Gateway]
    auth[Auth Service]
    profile[Profile Service]
    catalog[Catalog Service]
    order[Order Service]
    db[(Main Database)]
    cache[(Cache)]
    storage[(Object Storage)]
    
    user --> lb
    lb --> web1
    lb --> web2
    web1 --> api
    web2 --> api
    api --> auth
    api --> profile
    api --> catalog
    api --> order
    auth --> db
    profile --> db
    catalog --> db
    order --> db
    catalog --> cache
    catalog --> storage
    
    style user fill:#f9f,stroke:#333,stroke-width:2px
    style lb fill:#bbf,stroke:#333,stroke-width:2px
    style web1 fill:#dff,stroke:#333,stroke-width:2px
    style web2 fill:#dff,stroke:#333,stroke-width:2px
    style api fill:#ffd,stroke:#333,stroke-width:2px
    style auth fill:#dfd,stroke:#333,stroke-width:2px
    style profile fill:#dfd,stroke:#333,stroke-width:2px
    style catalog fill:#dfd,stroke:#333,stroke-width:2px
    style order fill:#dfd,stroke:#333,stroke-width:2px
    style db fill:#ffe,stroke:#333,stroke-width:2px
    style cache fill:#ffe,stroke:#333,stroke-width:2px
    style storage fill:#ffe,stroke:#333,stroke-width:2px"""
    
    container.markdown("## System Design Template")
    container.markdown(f"```mermaid\n{mermaid_code}\n```")
    
    # Also provide the code for copying
    with container.expander("Mermaid Code"):
        container.code(mermaid_code, language="mermaid")
        
    return mermaid_code

def get_system_design_template():
    """Return system design template as text"""
    mermaid_code = """flowchart TD
    user([User/Client])
    lb[Load Balancer]
    web1[Web Server 1]
    web2[Web Server 2]
    api[API Gateway]
    auth[Auth Service]
    profile[Profile Service]
    catalog[Catalog Service]
    order[Order Service]
    db[(Main Database)]
    cache[(Cache)]
    storage[(Object Storage)]
    
    user --> lb
    lb --> web1
    lb --> web2
    web1 --> api
    web2 --> api
    api --> auth
    api --> profile
    api --> catalog
    api --> order
    auth --> db
    profile --> db
    catalog --> db
    order --> db
    catalog --> cache
    catalog --> storage
    
    style user fill:#f9f,stroke:#333,stroke-width:2px
    style lb fill:#bbf,stroke:#333,stroke-width:2px
    style web1 fill:#dff,stroke:#333,stroke-width:2px
    style web2 fill:#dff,stroke:#333,stroke-width:2px
    style api fill:#ffd,stroke:#333,stroke-width:2px
    style auth fill:#dfd,stroke:#333,stroke-width:2px
    style profile fill:#dfd,stroke:#333,stroke-width:2px
    style catalog fill:#dfd,stroke:#333,stroke-width:2px
    style order fill:#dfd,stroke:#333,stroke-width:2px
    style db fill:#ffe,stroke:#333,stroke-width:2px
    style cache fill:#ffe,stroke:#333,stroke-width:2px
    style storage fill:#ffe,stroke:#333,stroke-width:2px"""
    return mermaid_code