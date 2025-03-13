"""
Ollama Client - Module for interacting with Ollama API
"""
import json
import requests
from typing import Dict, Any, Optional, List
import logging
import sys

class OllamaClient:
    """Client for interacting with Ollama API running in Docker"""
    
    def __init__(self, base_url: str, model_name: str):
        """
        Initialize the Ollama client
        
        Args:
            base_url: Base URL for the Ollama API (e.g., http://localhost:11434)
            model_name: Name of the model to use (e.g., llama3, mistral)
        """
        self.base_url = base_url.rstrip('/')
        self.model_name = model_name
        self.logger = logging.getLogger(__name__)
        self.generate_endpoint = f"{self.base_url}/api/generate"
        
        # Set up console logging for debugging
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
        # Verify connection
        self._verify_connection()
    
    def _verify_connection(self) -> bool:
        """
        Verify connection to Ollama API
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name") for m in models]
                self.logger.info(f"Successfully connected to Ollama API at {self.base_url}")
                self.logger.info(f"Available models: {model_names}")
                
                # Check if our model exists
                if not any(self.model_name in name for name in model_names):
                    self.logger.warning(f"Model '{self.model_name}' not found in available models. Will attempt to use '{self.model_name}:latest' or first available model.")
                    # If our specific model isn't available, try with :latest or use the first available model
                    if model_names:
                        if f"{self.model_name}:latest" in model_names:
                            self.model_name = f"{self.model_name}:latest"
                        else:
                            self.model_name = model_names[0].split(':')[0]  # Use base name of first model
                        self.logger.info(f"Using model: {self.model_name}")
                
                return True
            else:
                self.logger.warning(f"Connection to Ollama API failed with status code {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to connect to Ollama API: {e}")
            return False
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate text using the Ollama model
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt for context
            
        Returns:
            str: Generated text response
        """
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        self.logger.info(f"Sending request to Ollama API with model {self.model_name}")
        self.logger.info(f"Endpoint: {self.generate_endpoint}")
        self.logger.info(f"Payload: {json.dumps(payload)}")
        
        try:
            headers = {"Content-Type": "application/json"}
            response = requests.post(self.generate_endpoint, json=payload, headers=headers)
            
            self.logger.info(f"Response status code: {response.status_code}")
            if response.status_code != 200:
                self.logger.error(f"Error response: {response.text}")
                response.raise_for_status()
                
            result = response.json()
            self.logger.info("Response received successfully")
            
            return result.get("response", "")
        except requests.RequestException as e:
            self.logger.error(f"Error during API call to Ollama: {e}")
            raise RuntimeError(f"Failed to generate text with Ollama: {e}")
    
    def generate_flow_description(self, description: str) -> Dict[str, Any]:
        """
        Generate a flow diagram description from a text prompt
        
        Args:
            description: User description of the desired flow diagram
            
        Returns:
            Dict[str, Any]: Structured data for flow diagram generation
        """
        system_prompt = """
        You are a specialized flow diagram creation assistant. Your task is to convert
        user descriptions into structured JSON that represents flow diagrams.
        
        Output a valid JSON object with the following structure:
        {
            "nodes": [
                {"id": "node1", "label": "Node Label", "type": "process|decision|start|end|io", "description": "Optional description"},
                ...
            ],
            "edges": [
                {"from": "node1", "to": "node2", "label": "Connection Label", "type": "normal|conditional|feedback"},
                ...
            ],
            "title": "Diagram Title",
            "description": "Overall diagram description",
            "animations": [
                {"element": "node1", "effect": "fadeIn|highlight|pulse", "duration": 1.0, "order": 1},
                {"element": "edge_node1_node2", "effect": "draw|highlight", "duration": 0.8, "order": 2},
                ...
            ]
        }
        
        Ensure all IDs are unique and all references are valid. Include meaningful animations
        that help illustrate the flow sequence.
        """
        
        prompt = f"""
        Create a detailed flow diagram from the following description:
        
        {description}
        
        Respond only with the JSON structure defined in the system prompt.
        """
        
        response = self.generate(prompt, system_prompt)
        
        # Extract JSON from the response
        try:
            # Find JSON-like content in the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                self.logger.info(f"Extracted JSON: {json_str}")
                diagram_data = json.loads(json_str)
                
                # Validate the basic structure
                required_keys = ["nodes", "edges", "title"]
                if all(key in diagram_data for key in required_keys):
                    return diagram_data
                else:
                    missing = [key for key in required_keys if key not in diagram_data]
                    self.logger.error(f"Missing required keys in diagram data: {missing}")
            
            # If we couldn't parse JSON or it's invalid, try to create a basic structure
            self.logger.warning("Could not extract valid JSON from response, creating fallback structure")
            return self._create_fallback_diagram(description, response)
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON from Ollama response: {e}")
            return self._create_fallback_diagram(description, response)
    
    def _create_fallback_diagram(self, description: str, response: str) -> Dict[str, Any]:
        """
        Create a fallback diagram when JSON parsing fails
        
        Args:
            description: Original user description
            response: Raw response from Ollama
            
        Returns:
            Dict[str, Any]: Basic diagram structure
        """
        # Extract possible nodes from the response text
        lines = response.split('\n')
        potential_nodes = []
        for line in lines:
            line = line.strip()
            if line and len(line) > 3 and not line.startswith('{') and not line.startswith('}'):
                potential_nodes.append(line.split(':')[0] if ':' in line else line)
        
        # Limit to a reasonable number of distinct nodes
        potential_nodes = list(set([node.strip() for node in potential_nodes]))[:10]
        
        # Create a simple linear flow
        nodes = []
        edges = []
        
        # Start node
        nodes.append({
            "id": "start",
            "label": "Start",
            "type": "start",
            "description": "Beginning of the process"
        })
        
        # Add nodes from potential_nodes or create generic ones
        for i, node_text in enumerate(potential_nodes[:5] if potential_nodes else range(3)):
            node_id = f"node{i+1}"
            if isinstance(node_text, str):
                node_label = node_text[:30]  # Truncate long labels
            else:
                node_label = f"Process {i+1}"
                
            nodes.append({
                "id": node_id,
                "label": node_label,
                "type": "process",
                "description": f"Step {i+1} in the process"
            })
        
        # End node
        nodes.append({
            "id": "end",
            "label": "End",
            "type": "end",
            "description": "End of the process"
        })
        
        # Create edges to connect all nodes sequentially
        prev_id = "start"
        for i in range(len(nodes) - 2):  # Exclude start and end nodes
            current_id = f"node{i+1}"
            edges.append({
                "from": prev_id,
                "to": current_id,
                "label": f"Step {i+1}",
                "type": "normal"
            })
            prev_id = current_id
        
        # Connect last node to end
        edges.append({
            "from": prev_id,
            "to": "end",
            "label": "Complete",
            "type": "normal"
        })
        
        # Create simple animations
        animations = []
        for i, node in enumerate(nodes):
            animations.append({
                "element": node["id"],
                "effect": "fadeIn",
                "duration": 0.8,
                "order": i+1
            })
        
        for i, edge in enumerate(edges):
            animations.append({
                "element": f"edge_{edge['from']}_{edge['to']}",
                "effect": "draw",
                "duration": 0.5,
                "order": len(nodes) + i+1
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "title": "Flow Diagram",
            "description": description[:100] + "...",
            "animations": animations
        }