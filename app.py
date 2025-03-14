"""
Flow Diagram Animation Assistant - Main Streamlit Application
"""
import os
import streamlit as st
from dotenv import load_dotenv
from src.mermaid_generator import display_mermaid, export_mermaid
import time

# Import local modules
from src.ollama_client import OllamaClient
from src.diagram_generator import DiagramGenerator
from src.animation import animate_diagram
from src.utils.logger import setup_logger
from src.system_templates import display_system_design_template, get_system_design_template

# Load environment variables
load_dotenv()

# Setup logger
logger = setup_logger()

# Page configuration
st.set_page_config(
    page_title="Flow Diagram Animation Assistant",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
def load_css():
    """Load custom CSS"""
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #4F8BF9;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0F52BA;
        margin-bottom: 0.5rem;
    }
    .stButton button {
        background-color: #4F8BF9;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-size: 1rem;
    }
    .diagram-container {
        border: 1px solid #ccc;
        border-radius: 5px;
        padding: 1rem;
        background-color: white;
    }
    .chat-message {
        padding: 0.5rem;
        border-radius: 5px;
        margin-bottom: 0.5rem;
    }
    .user-message {
        background-color: #E1F5FE;
        text-align: right;
    }
    .assistant-message {
        background-color: #F1F1F1;
    }
    </style>
    """, unsafe_allow_html=True)

# Session state initialization
def init_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_diagram" not in st.session_state:
        st.session_state.current_diagram = None
    if "animation_speed" not in st.session_state:
        st.session_state.animation_speed = 1.0
    if "ollama_model" not in st.session_state:
        st.session_state.ollama_model = os.getenv("OLLAMA_MODEL_NAME", "llama2")
    if "animation_enabled" not in st.session_state:
        st.session_state.animation_enabled = True

# Initialize Ollama client
@st.cache_resource
def get_ollama_client():
    """Get or create Ollama client"""
    return OllamaClient(
        base_url=os.getenv("OLLAMA_API_BASE_URL", "http://localhost:11434"),
        model_name=st.session_state.ollama_model
    )

# Initialize diagram generator
@st.cache_resource
def get_diagram_generator():
    """Get or create diagram generator"""
    return DiagramGenerator()

# Main application UI
def main():
    """Main application interface"""
    load_css()
    init_session_state()
    
    # Sidebar
    with st.sidebar:
        st.markdown("<div class='sub-header'>Configuration</div>", unsafe_allow_html=True)
        
        # Model selection
        st.session_state.ollama_model = st.selectbox(
            "Select Ollama Model",
            ["llama2", "mistral", "gemma", "phi", "nous-hermes"],
            index=0
        )
        
        # Animation settings
        st.session_state.animation_enabled = st.checkbox("Enable Animation", value=True)
        st.session_state.animation_speed = st.slider(
            "Animation Speed",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1
        )
        
        # GIF export settings
        st.markdown("---")
        st.markdown("<div class='sub-header'>GIF Export Settings</div>", unsafe_allow_html=True)
        st.session_state.animation_duration = st.slider(
            "GIF Duration (seconds)",
            min_value=2.0,
            max_value=10.0,
            value=5.0,
            step=0.5
        )
        
        # About section
        st.markdown("---")
        st.markdown("<div class='sub-header'>About</div>", unsafe_allow_html=True)
        st.markdown(
            """
            This application generates animated flow diagrams using Ollama 
            models running locally in Docker. Simply describe what you want 
            and watch your flow diagrams come to life!
            """
        )
        
        # Credits
        st.markdown("---")
        st.markdown("Built with Streamlit and Ollama")
    
    # Main content
    st.markdown("<div class='main-header'>Flow Diagram Animation Assistant</div>", unsafe_allow_html=True)
    
    # Chat interface
    st.markdown("<div class='sub-header'>Chat Interface</div>", unsafe_allow_html=True)
    
    # Display chat messages
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        with st.chat_message(role):
            st.write(content)
    
    # Chat input
    prompt = st.chat_input("Describe the flow diagram you want to create...")
    
    if prompt:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get Ollama client and diagram generator
        ollama_client = get_ollama_client()
        diagram_generator = get_diagram_generator()
        
        # Show assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.write("Generating flow diagram...")
            
            # Process the user's request
            try:
                # Get response from Ollama
                with st.spinner("Thinking..."):
                    response = ollama_client.generate_flow_description(prompt)
                
                # Generate diagram
                with st.spinner("Creating diagram..."):
                    diagram = diagram_generator.generate(response)
                    st.session_state.current_diagram = diagram
                
                # Show success message
                message_placeholder.write("I've created a flow diagram based on your description!")
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": "I've created a flow diagram based on your description!"
                })
                
            except Exception as e:
                error_msg = f"Error generating diagram: {str(e)}"
                message_placeholder.write(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                logger.error(error_msg)
    
    # Diagram type selection
    diagram_type = st.radio(
        "Select Diagram Type",
        ["Interactive", "Mermaid", "System Design Template"],
        horizontal=True
    )
    
    # Display diagram if it exists
    if st.session_state.current_diagram:
        st.markdown("<div class='sub-header'>Flow Diagram</div>", unsafe_allow_html=True)
        
        diagram_container = st.container()
        with diagram_container:
            st.markdown("<div class='diagram-container'>", unsafe_allow_html=True)
            
            if diagram_type == "Interactive":
                # Show with or without animation based on settings
                if st.session_state.animation_enabled:
                    animate_diagram(
                        st.session_state.current_diagram, 
                        speed=st.session_state.animation_speed,
                        container=diagram_container
                    )
                else:
                    diagram_generator.display(st.session_state.current_diagram)
            elif diagram_type == "Mermaid":
                display_mermaid(st.session_state.current_diagram)
            else:  # System Design Template
                display_system_design_template(container=diagram_container)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Export options
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            try:
                png_data = diagram_generator.export_as_png(st.session_state.current_diagram)
                st.download_button(
                    "Download as PNG",
                    data=png_data,
                    file_name="flow_diagram.png",
                    mime="image/png"
                )
            except Exception as e:
                st.error(f"PNG export error: {str(e)}")
                
        with col2:
            try:
                svg_data = diagram_generator.export_as_svg(st.session_state.current_diagram)
                st.download_button(
                    "Download as SVG",
                    data=svg_data,
                    file_name="flow_diagram.svg",
                    mime="image/svg+xml"
                )
            except Exception as e:
                st.error(f"SVG export error: {str(e)}")
                
        with col3:
            try:
                from src.gif_export import export_as_gif
                
                animation_duration = st.session_state.get("animation_duration", 5.0)
                
                gif_data = export_as_gif(
                    st.session_state.current_diagram,
                    duration=animation_duration,
                    fps=10
                )
                
                st.download_button(
                    "Download as GIF",
                    data=gif_data,
                    file_name="flow_diagram.gif",
                    mime="image/gif"
                )
            except Exception as e:
                st.error(f"GIF export error: {str(e)}")
                
        with col4:
            if diagram_type == "System Design Template":
                st.download_button(
                    "Download Template",
                    data=get_system_design_template(),
                    file_name="system_design_template.mmd",
                    mime="text/plain"
                )
            else:
                try:
                    mermaid_data = export_mermaid(st.session_state.current_diagram)
                    st.download_button(
                        "Download as Mermaid",
                        data=mermaid_data,
                        file_name="flow_diagram.mmd",
                        mime="text/plain"
                    )
                except Exception as e:
                    st.error(f"Mermaid export error: {str(e)}")

if __name__ == "__main__":
    main()