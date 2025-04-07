from typing import Dict, List, Any
from models.llama_interface import LlamaInterface

class QualityAssuranceAgent:
    def __init__(self):
        """Initialize the Quality Assurance Agent"""
        self.llm = LlamaInterface()
        
        # Set specialized system prompt for QA
        self.llm.set_system_prompt("""You are a Quality Assurance AI assistant that specializes in 
        reviewing data visualizations and ensuring they meet the user's requirements. You can identify 
        issues in visualizations and suggest improvements.""")
    
    def review_visualization(self, requirements: str, viz_result: Dict[str, Any], data_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Review the visualization and provide feedback"""
        # Generate explanation
        explanation = self.llm.generate_explanation(
            data_summary,
            viz_result.get("visualization_info", {})
        )
        
        # Check for potential issues
        issues = self._check_for_issues(requirements, viz_result, data_summary)
        
        result = {
            "explanation": explanation,
            "issues": issues,
            "quality_score": self._calculate_quality_score(issues)
        }
        
        return result
    
    def _check_for_issues(self, requirements: str, viz_result: Dict[str, Any], data_summary: Dict[str, Any]) -> List[Dict[str, str]]:
        """Check for potential issues in the visualization"""
        issues = []
        
        # Check if visualization type matches data
        viz_info = viz_result.get("visualization_info", {})
        viz_type = viz_info.get("type", "")
        
        # Check for pie chart with too many categories
        if viz_type == "pie" and "categorical_summary" in data_summary:
            x_axis = viz_info.get("x_axis", "")
            if x_axis in data_summary.get("categorical_summary", {}):
                unique_values = data_summary["categorical_summary"][x_axis].get("unique_values", 0)
                if unique_values > 7:
                    issues.append({
                        "severity": "warning",
                        "message": f"Pie chart has {unique_values} categories, which may be too many for effective visualization. Consider using a bar chart instead."
                    })
        
        # Check for bar chart with too many categories
        if viz_type == "bar" and "categorical_summary" in data_summary:
            x_axis = viz_info.get("x_axis", "")
            if x_axis in data_summary.get("categorical_summary", {}):
                unique_values = data_summary["categorical_summary"][x_axis].get("unique_values", 0)
                if unique_values > 15:
                    issues.append({
                        "severity": "warning",
                        "message": f"Bar chart has {unique_values} categories, which may be difficult to read. Consider filtering to show only top categories."
                    })
        
        # Check for scatter plot without color encoding for large datasets
        if viz_type == "scatter" and data_summary.get("row_count", 0) > 50:
            if not viz_info.get("color"):
                issues.append({
                    "severity": "suggestion",
                    "message": "For scatter plots with many data points, using color to encode an additional variable can reveal patterns."
                })
        
        # Check if requirements mention something not in visualization
        # This is a simplified check, a real system would do more sophisticated NLP
        important_keywords = ["time", "trend", "compare", "distribution", "relationship", "correlation"]
        for keyword in important_keywords:
            if keyword in requirements.lower():
                if keyword == "time" and viz_type != "line" and viz_type != "area":
                    issues.append({
                        "severity": "suggestion",
                        "message": f"Requirements mention '{keyword}' which often works best with a line chart or area chart."
                    })
                elif keyword == "trend" and viz_type != "line":
                    issues.append({
                        "severity": "suggestion",
                        "message": f"Requirements mention '{keyword}' which often works best with a line chart."
                    })
                elif keyword == "distribution" and viz_type != "histogram" and viz_type != "density":
                    issues.append({
                        "severity": "suggestion",
                        "message": f"Requirements mention '{keyword}' which often works best with a histogram or density plot."
                    })
                elif keyword == "correlation" and viz_type != "scatter":
                    issues.append({
                        "severity": "suggestion",
                        "message": f"Requirements mention '{keyword}' which often works best with a scatter plot."
                    })
        
        return issues
    
    def _calculate_quality_score(self, issues: List[Dict[str, str]]) -> float:
        """Calculate a quality score based on issues"""
        # Start with perfect score
        score = 10.0
        
        # Deduct for each issue based on severity
        for issue in issues:
            if issue["severity"] == "error":
                score -= 2.0
            elif issue["severity"] == "warning":
                score -= 1.0
            elif issue["severity"] == "suggestion":
                score -= 0.5
        
        # Ensure score doesn't go below 0
        return max(0, score)
