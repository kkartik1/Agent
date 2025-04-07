import json
import requests
from typing import Dict, List, Any, Optional

class LlamaInterface:
    def __init__(self, base_url: str = "http://localhost:11434"):
        """Initialize Llama interface to communicate with Ollama API"""
        self.base_url = base_url
        self.api_generate = f"{base_url}/api/generate"
        self.model = "llama3"  # Default model
        self.system_prompt = """You are a helpful AI assistant specialized in data analysis and visualization.
        Your task is to help users understand and visualize their data effectively."""
    
    def set_model(self, model_name: str) -> None:
        """Set the Llama model to use"""
        self.model = model_name
    
    def set_system_prompt(self, prompt: str) -> None:
        """Set the system prompt for the model"""
        self.system_prompt = prompt
    
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Generate a response using the Llama model"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "system": self.system_prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False
            }
            
            response = requests.post(self.api_generate, json=payload)
            response.raise_for_status()
            return response.json()["response"]
        except requests.exceptions.RequestException as e:
            print(f"Error communicating with Ollama: {e}")
            return f"Error generating response: {str(e)}"
    
    def schema_mapping(self, columns: List[str]) -> Dict[str, str]:
        """Map technical column names to business entities"""
        prompt = f"""I have a dataset with the following column names:
        {', '.join(columns)}
        
        Please map these technical column names to their likely business entities.
        Return your response as valid JSON with the technical name as key and business entity as value.
        Example format: {{"technical_name": "business_entity"}}"""
        
        response = self.generate(prompt)
        
        # Try to extract JSON from the response
        try:
            # Look for JSON patterns in the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback: create simple mapping
                return {col: col.replace('_', ' ').title() for col in columns}
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {col: col.replace('_', ' ').title() for col in columns}
    
    def interpret_requirements(self, requirements: str, schema_mapping: Dict[str, str], sample_data: Dict[str, List]) -> Dict[str, Any]:
        """Interpret user requirements and convert to data processing instructions"""
        sample_data_str = json.dumps(sample_data, indent=2)
        schema_str = json.dumps(schema_mapping, indent=2)
        
        prompt = f"""I have a dataset with the following schema mapping:
        {schema_str}
        
        Here's a sample of the data:
        {sample_data_str}
        
        The user has the following requirements:
        "{requirements}"
        
        Please analyze the requirements and provide detailed instructions for:
        1. Data filtering (if any)
        2. Data grouping (if any)
        3. Aggregation methods (if any)
        4. Visualization type that best suits the data and requirements
        5. Columns to use for the visualization
        
        Return your answer as a valid JSON object with the following structure:
        {{
            "filters": [{{
                "column": "column_name",
                "operation": "==, >, <, in, etc.",
                "value": "filter_value"
            }}],
            "groupby": ["column1", "column2"],
            "aggregation": {{
                "method": "sum, mean, count, etc.",
                "column": "column_to_aggregate"
            }},
            "visualization": {{
                "type": "bar, line, scatter, pie, etc.",
                "x_axis": "column_name",
                "y_axis": "column_name",
                "color": "column_name (optional)",
                "title": "suggested chart title"
            }}
        }}"""
        
        response = self.generate(prompt)
        
        # Extract JSON from the response
        try:
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                raise ValueError("Could not extract valid JSON from LLM response")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing LLM response: {e}")
            print(f"Raw response: {response}")
            return {
                "filters": [],
                "groupby": [],
                "aggregation": {"method": "sum", "column": ""},
                "visualization": {"type": "bar", "x_axis": "", "y_axis": "", "title": "Data Visualization"}
            }
    
    def generate_explanation(self, data_summary: Dict[str, Any], visualization_info: Dict[str, Any]) -> str:
        """Generate an explanation of the visualization"""
        prompt = f"""I've created a visualization with the following characteristics:
        - Type: {visualization_info.get('type', 'chart')}
        - Title: {visualization_info.get('title', 'Data Visualization')}
        - X-axis: {visualization_info.get('x_axis', '')}
        - Y-axis: {visualization_info.get('y_axis', '')}
        
        Data summary:
        {json.dumps(data_summary, indent=2)}
        
        Please provide a concise explanation of what this visualization shows, any patterns or insights that can be observed,
        and how it addresses the user's requirements. Keep the explanation clear and non-technical.
        """
        
        return self.generate(prompt, temperature=0.7, max_tokens=300)
