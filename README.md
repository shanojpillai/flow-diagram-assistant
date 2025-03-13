# Flow Diagram Animation Assistant

A Python application that generates animated flow diagrams from natural language descriptions using Ollama models running locally in Docker.

## Features

- Chat interface powered by Streamlit
- Automatic flow diagram generation from descriptions
- Animated diagram rendering with customizable transitions
- Integration with Ollama models running in Docker
- Export diagrams to PNG and SVG formats
- Customizable animation speed and effects

## Requirements

- Python 3.8+
- Docker with Ollama container running
- Dependencies listed in `requirements.txt`

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/flow-diagram-assistant.git
   cd flow-diagram-assistant
   ```

2. Set up the virtual environment:
   ```
   # On Linux/macOS
   ./scripts/setup_env.sh
   
   # On Windows
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Ensure your Ollama Docker container is running:
   ```
   docker run -d --name ollama -p 11434:11434 ollama/ollama
   ```

4. Pull your preferred model in Ollama:
   ```
   docker exec -it ollama ollama pull llama2
   ```

## Usage

1. Activate the virtual environment if not already activated:
   ```
   # On Linux/macOS
   source venv/bin/activate
   
   # On Windows
   venv\Scripts\activate
   ```

2. Start the application:
   ```
   streamlit run app.py
   ```

3. Open your browser at `http://localhost:8501`

4. Enter a description of the flow diagram you want to create in the chat interface.

## Configuration

You can configure the application through environment variables in the `.env` file:

```
# Ollama API Configuration
OLLAMA_API_BASE_URL=http://localhost:11434
OLLAMA_MODEL_NAME=llama2

# App Configuration
APP_DEBUG=True
LOG_LEVEL=INFO
CACHE_DIR=./cache

# Animation Settings
ANIMATION_ENABLED=True
ANIMATION_SPEED=1.0
```

## Project Structure

```
flow-diagram-assistant/
├── .env                    # Environment variables
├── .gitignore              # Git ignore file
├── README.md               # Project documentation
├── requirements.txt        # Python dependencies
├── app.py                  # Main Streamlit application
├── src/                    # Source code
│   ├── ollama_client.py    # Client to interact with Ollama API
│   ├── diagram_generator.py # Flow diagram generation logic
│   ├── animation.py        # Animation utilities for diagrams
│   └── utils/              # Utility modules
│       └── logger.py       # Logging utility
├── scripts/                # Utility scripts
│   └── setup_env.sh        # Environment setup script
├── logs/                   # Log files
└── cache/                  # Cache directory
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.