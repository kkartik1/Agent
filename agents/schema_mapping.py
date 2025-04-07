from typing import Dict, List, Any
import pandas as pd
from utils.file_handler import read_file, get_file_headers
from models.llama_interface import LlamaInterface
from models.knowledge_base import KnowledgeBase

class SchemaMapperAgent:
    def __init__(self):
        """Initialize the Schema Mapping Agent"""
        self.llm = LlamaInterface()
        self.knowledge_base = KnowledgeBase()
        
        # Set specialized system prompt for schema mapping
        self.llm.set_system_prompt("""You are a Schema Mapping AI assistant that specializes in converting 
        technical database column names to business-friendly entity names. You understand common naming 
        conventions in databases and can map them to their likely business meanings.""")
    
    def _check_knowledge_base(self, columns: List[str]) -> Dict[str, str]:
        """Check if mappings exist in knowledge base"""
        mappings = {}
        for column in columns:
            mappings[column] = self.knowledge_base.get_mapping(column)
        return mappings
    
    def _get_llm_mappings(self, columns: List[str]) -> Dict[str, str]:
        """Get mappings from LLM for columns not in knowledge base"""
        return self.llm.schema_mapping(columns)
    
    def map_schema(self, filepath: str) -> Dict[str, str]:
        """Map technical column names to business entities"""
        # Get column headers from file
        columns = get_file_headers(filepath)
        
        # First check knowledge base for existing mappings
        kb_mappings = self._check_knowledge_base(columns)
        
        # For columns without confident mappings, use LLM
        columns_for_llm = [col for col in columns if kb_mappings[col] == col.replace('_', ' ').title()]
        
        if columns_for_llm:
            llm_mappings = self._get_llm_mappings(columns_for_llm)
            
            # Update mappings with LLM results
            for col, mapping in llm_mappings.items():
                if col in kb_mappings:
                    kb_mappings[col] = mapping
            
            # Add new mappings to knowledge base
            self.knowledge_base.add_mappings(llm_mappings)
        
        return kb_mappings
    
    def get_sample_data(self, filepath: str, rows: int = 5) -> Dict[str, List]:
        """Get a sample of the data for providing context to other agents"""
        df = read_file(filepath)
        sample = df.head(rows)
        
        # Convert to dictionary for easier JSON serialization
        sample_dict = {}
        for column in sample.columns:
            sample_dict[column] = sample[column].tolist()
        
        return sample_dict
    
    def add_feedback(self, technical: str, business: str, positive: bool) -> None:
        """Add user feedback to improve mappings"""
        self.knowledge_base.add_feedback(technical, business, positive)
