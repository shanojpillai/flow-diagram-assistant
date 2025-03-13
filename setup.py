"""
Setup script for Flow Diagram Animation Assistant
"""
from setuptools import setup, find_packages
import os
from pathlib import Path

# Read the contents of your README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read version from __init__.py
with open(os.path.join("src", "__init__.py"), "r") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"').strip("'")
            break
    else:
        version = "0.1.0"

setup(
    name="flow-diagram-assistant",
    version=version,
    description="Generate animated flow diagrams using Ollama models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/flow-diagram-assistant",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "streamlit>=1.18.0",
        "python-dotenv>=0.19.0",
        "requests>=2.28.0",
        "pydantic>=1.10.0",
        "graphviz>=0.20.0",
        "pydot>=1.4.2",
        "networkx>=2.8.0",
        "matplotlib>=3.6.0",
        "plotly>=5.10.0",
        "streamlit-agraph>=0.0.40",
        "streamlit-elements>=0.1.0",
        "streamlit-lottie>=0.0.3",
        "plotly-express>=0.4.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
)