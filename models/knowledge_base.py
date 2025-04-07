import json
import os
from typing import Dict, List, Tuple, Set

class KnowledgeBase:
    def __init__(self, storage_path: str = "data/knowledge_base.json"):
        """Initialize the knowledge base for schema mappings"""
        self.storage_path = storage_path
        self.mappings = {}
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        
        # Load existing knowledge base if it exists
        if os.path.exists(storage_path):
            try:
                with open(storage_path, 'r') as f:
                    self.mappings = json.load(f)
            except json.JSONDecodeError:
                print(f"Error loading knowledge base from {storage_path}. Starting with empty knowledge base.")
    
    def save(self) -> None:
        """Save the knowledge base to disk"""
        with open(self.storage_path, 'w') as f:
            json.dump(self.mappings, f, indent=2)
    
    def add_mappings(self, mappings: Dict[str, str], confidence: float = 0.8) -> None:
        """Add new mappings to the knowledge base"""
        for technical, business in mappings.items():
            if technical not in self.mappings:
                self.mappings[technical] = {
                    "mappings": [{
                        "business_entity": business,
                        "confidence": confidence,
                        "count": 1
                    }]
                }
            else:
                # Check if this business entity already exists
                found = False
                for mapping in self.mappings[technical]["mappings"]:
                    if mapping["business_entity"].lower() == business.lower():
                        mapping["count"] += 1
                        mapping["confidence"] = min(1.0, mapping["confidence"] + 0.05)
                        found = True
                        break
                
                if not found:
                    self.mappings[technical]["mappings"].append({
                        "business_entity": business,
                        "confidence": confidence,
                        "count": 1
                    })
        
        # Save updated knowledge base
        self.save()
    
    def get_mapping(self, technical: str) -> str:
        """Get the most confident business entity mapping for a technical column name"""
        if technical not in self.mappings:
            return technical.replace('_', ' ').title()
        
        # Find mapping with highest confidence
        mappings = self.mappings[technical]["mappings"]
        best_mapping = max(mappings, key=lambda x: (x["confidence"], x["count"]))
        
        return best_mapping["business_entity"]
    
    def get_all_mappings(self, technical: str) -> List[Dict]:
        """Get all mappings for a technical column name"""
        if technical not in self.mappings:
            return [{
                "business_entity": technical.replace('_', ' ').title(),
                "confidence": 0.5,
                "count": 0
            }]
        
        return self.mappings[technical]["mappings"]
    
    def add_feedback(self, technical: str, business: str, positive: bool) -> None:
        """Add user feedback to improve mappings"""
        if technical not in self.mappings:
            confidence = 0.6 if positive else 0.4
            self.mappings[technical] = {
                "mappings": [{
                    "business_entity": business,
                    "confidence": confidence,
                    "count": 1
                }]
            }
            self.save()
            return
        
        found = False
        for mapping in self.mappings[technical]["mappings"]:
            if mapping["business_entity"].lower() == business.lower():
                if positive:
                    mapping["confidence"] = min(1.0, mapping["confidence"] + 0.1)
                else:
                    mapping["confidence"] = max(0.1, mapping["confidence"] - 0.1)
                mapping["count"] += 1
                found = True
                break
        
        if not found and positive:
            self.mappings[technical]["mappings"].append({
                "business_entity": business,
                "confidence": 0.6,
                "count": 1
            })
        
        self.save()
