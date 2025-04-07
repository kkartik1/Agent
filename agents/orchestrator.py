from typing import Dict, List, Any
import os
import json
import uuid
from agents.schema_mapping import SchemaMapperAgent
from agents.data_processing import DataProcessingAgent
from agents.visualization import VisualizationAgent
from agents.quality_assurance import QualityAssuranceAgent

class Orchestrator:
    def __init__(self):
        """Initialize the Orchestrator with all agents"""
        self.schema_mapper = SchemaMapperAgent()
        self.data_processor = DataProcessingAgent()
        self.visualizer = VisualizationAgent()
        self.qa_agent = QualityAssuranceAgent()
        
        # Store for visualization results
        self.visualization_store = {}
        
        # Ensure store directory exists
        os.makedirs("data/visualizations", exist_ok=True)
    
    def process_file(self, filepath: str) -> Dict[str, Any]:
        """Process an uploaded file and return initial schema information"""
        # Extract schema mappings
        schema_mappings = self.schema_mapper.map_schema(filepath)
        
        # Get sample data
        sample_data = self.schema_mapper.get_sample_data(filepath)
        
        return {
            "file_path": filepath,
            "schema_mappings": schema_mappings,
            "sample_data": sample_data
        }
    
    def process_request(self, filepath: str, requirements: str) -> Dict[str, Any]:
        """Process a user request through the agent pipeline"""
        try:
            # 1. Get schema mappings
            schema_mappings = self.schema_mapper.map_schema(filepath)
            
            # 2. Get sample data for context
            sample_data = self.schema_mapper.get_sample_data(filepath)
            
            # 3. Process data according to requirements
            processed_data = self.data_processor.process_data(
                filepath, 
                requirements, 
                schema_mappings, 
                sample_data
            )
            
            # 4. Create visualization
            visualization = self.visualizer.create_visualization(
                processed_data["data"],
                processed_data["visualization_info"]
            )
            
            # 5. Review visualization through QA
            qa_result = self.qa_agent.review_visualization(
                requirements,
                visualization,
                processed_data["data_summary"]
            )
            
            # 6. Combine results
            result = {
                "viz_id": visualization["viz_id"],
                "visualization_html": visualization["visualization_html"],
                "explanation": qa_result["explanation"],
                "issues": qa_result["issues"],
                "quality_score": qa_result["quality_score"]
            }
            
            # Store the full result for later retrieval
            self._store_visualization(visualization["viz_id"], {
                **result,
                "processed_data": processed_data,
                "requirements": requirements,
                "schema_mappings": schema_mappings
            })
            
            return result
            
        except Exception as e:
            print(f"Error in orchestration: {e}")
            return {"error": str(e)}
    
    def _store_visualization(self, viz_id: str, data: Dict[str, Any]) -> None:
        """Store visualization data for later retrieval"""
        self.visualization_store[viz_id] = data
        
        # Also save to disk as backup
        try:
            with open(f"data/visualizations/{viz_id}.json", 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving visualization data: {e}")
    
    def get_visualization(self, viz_id: str) -> Dict[str, Any]:
        """Retrieve a stored visualization"""
        if viz_id in self.visualization_store:
            return self.visualization_store[viz_id]
        
        # Try to load from disk
        try:
            with open(f"data/visualizations/{viz_id}.json", 'r') as f:
                data = json.load(f)
                self.visualization_store[viz_id] = data
                return data
        except:
            return {"error": "Visualization not found"}
    
    def get_downloadable_html(self, viz_id: str) -> str:
        """Get downloadable HTML for a visualization"""
        viz_data = self.get_visualization(viz_id)
        
        if "error" in viz_data:
            return f"<html><body><h1>Error</h1><p>{viz_data['error']}</p></body></html>"
        
        return self.visualizer.get_downloadable_html(viz_id, viz_data)
