from typing import Dict, List, Any
import pandas as pd
import uuid
import json
import altair as alt
from models.llama_interface import LlamaInterface

class VisualizationAgent:
    def __init__(self):
        """Initialize the Visualization Agent"""
        self.llm = LlamaInterface()
        
        # Set specialized system prompt for visualization generation
        self.llm.set_system_prompt("""You are a Data Visualization AI assistant that specializes in 
        creating effective visualizations using Altair. You understand data visualization best practices 
        and can generate code to visualize data in the most informative way.""")
    
    def create_visualization(self, data: List[Dict[str, Any]], visualization_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create a visualization based on the processed data and visualization info"""
        if not data or not visualization_info:
            return {"error": "Insufficient data or visualization information"}
        
        # Convert data to DataFrame
        df = pd.DataFrame(data)
        
        # Generate visualization
        chart_html = self._generate_altair_chart(df, visualization_info)
        
        # Generate a unique ID for this visualization
        viz_id = str(uuid.uuid4())
        
        return {
            "viz_id": viz_id,
            "visualization_html": chart_html,
            "visualization_info": visualization_info
        }
    
    def _generate_altair_chart(self, df: pd.DataFrame, viz_info: Dict[str, Any]) -> str:
        """Generate an Altair chart based on visualization info"""
        chart_type = viz_info.get("type", "bar").lower()
        x_axis = viz_info.get("x_axis", "")
        y_axis = viz_info.get("y_axis", "")
        color = viz_info.get("color", None)
        title = viz_info.get("title", "Data Visualization")
        
        # Handle missing axis
        if not x_axis and df.columns.any():
            x_axis = df.columns[0]
        if not y_axis and len(df.columns) > 1:
            for col in df.columns:
                if col != x_axis and pd.api.types.is_numeric_dtype(df[col]):
                    y_axis = col
                    break
            if not y_axis and len(df.columns) > 1:
                y_axis = df.columns[1]
        
        try:
            # Define base chart with common properties
            base = alt.Chart(df).properties(
                title=title,
                width=600,
                height=400
            )
            
            # Create chart based on type
            if chart_type == "bar":
                chart = self._create_bar_chart(base, x_axis, y_axis, color)
            elif chart_type == "line":
                chart = self._create_line_chart(base, x_axis, y_axis, color)
            elif chart_type == "scatter":
                chart = self._create_scatter_chart(base, x_axis, y_axis, color)
            elif chart_type == "pie":
                chart = self._create_pie_chart(base, x_axis, y_axis)
            elif chart_type == "area":
                chart = self._create_area_chart(base, x_axis, y_axis, color)
            else:
                # Default to bar chart
                chart = self._create_bar_chart(base, x_axis, y_axis, color)
            
            # Convert chart to HTML
            chart_html = chart.to_html()
            return chart_html
            
        except Exception as e:
            print(f"Error generating chart: {e}")
            # Return a simple error message as HTML
            return f"""
            <div style="color: red; padding: 20px; border: 1px solid #ddd; text-align: center;">
                <h3>Error Generating Visualization</h3>
                <p>{str(e)}</p>
            </div>
            """
    
    def _create_bar_chart(self, base, x_axis, y_axis, color=None):
        """Create a bar chart"""
        if color:
            chart = base.mark_bar().encode(
                x=alt.X(x_axis, title=x_axis),
                y=alt.Y(y_axis, title=y_axis),
                color=alt.Color(color, title=color)
            )
        else:
            chart = base.mark_bar().encode(
                x=alt.X(x_axis, title=x_axis),
                y=alt.Y(y_axis, title=y_axis)
            )
        return chart
    
    def _create_line_chart(self, base, x_axis, y_axis, color=None):
        """Create a line chart"""
        if color:
            chart = base.mark_line().encode(
                x=alt.X(x_axis, title=x_axis),
                y=alt.Y(y_axis, title=y_axis),
                color=alt.Color(color, title=color)
            )
        else:
            chart = base.mark_line().encode(
                x=alt.X(x_axis, title=x_axis),
                y=alt.Y(y_axis, title=y_axis)
            )
        return chart
    
    def _create_scatter_chart(self, base, x_axis, y_axis, color=None):
        """Create a scatter plot"""
        if color:
            chart = base.mark_circle().encode(
                x=alt.X(x_axis, title=x_axis),
                y=alt.Y(y_axis, title=y_axis),
                color=alt.Color(color, title=color)
            )
        else:
            chart = base.mark_circle().encode(
                x=alt.X(x_axis, title=x_axis),
                y=alt.Y(y_axis, title=y_axis)
            )
        return chart
    
    def _create_pie_chart(self, base, x_axis, y_axis):
        """Create a pie chart"""
        chart = base.mark_arc().encode(
            theta=alt.Theta(field=y_axis, type="quantitative"),
            color=alt.Color(field=x_axis, type="nominal")
        )
        return chart
    
    def _create_area_chart(self, base, x_axis, y_axis, color=None):
        """Create an area chart"""
        if color:
            chart = base.mark_area().encode(
                x=alt.X(x_axis, title=x_axis),
                y=alt.Y(y_axis, title=y_axis),
                color=alt.Color(color, title=color)
            )
        else:
            chart = base.mark_area().encode(
                x=alt.X(x_axis, title=x_axis),
                y=alt.Y(y_axis, title=y_axis)
            )
        return chart
    
    def get_downloadable_html(self, viz_id: str, full_data: Dict[str, Any]) -> str:
        """Generate a standalone HTML file for the visualization"""
        chart_html = full_data.get("visualization_html", "")
        title = full_data.get("visualization_info", {}).get("title", "Data Visualization")
        explanation = full_data.get("explanation", "")
        
        html_template = f"""<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
                .container {{ max-width: 1000px; margin: 0 auto; }}
                .visualization {{ margin: 30px 0; }}
                .explanation {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; }}
                h1 {{ color: #333; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{title}</h1>
                
                <div class="visualization">
                    {chart_html}
                </div>
                
                <div class="explanation">
                    <h2>Explanation</h2>
                    <p>{explanation}</p>
                </div>
                
                <div class="footer">
                    <p><small>Generated on {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</small></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_template
