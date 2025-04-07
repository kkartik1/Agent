from typing import Dict, List, Any, Optional
import pandas as pd
from utils.file_handler import read_file
from models.llama_interface import LlamaInterface

class DataProcessingAgent:
    def __init__(self):
        """Initialize the Data Processing Agent"""
        self.llm = LlamaInterface()
        
        # Set specialized system prompt for data processing
        self.llm.set_system_prompt("""You are a Data Processing AI assistant that specializes in 
        understanding natural language requirements and converting them to precise data operations.
        You can interpret filtering, grouping, and aggregation requirements and translate them to 
        pandas operations.""")
    
    def process_data(self, filepath: str, requirements: str, schema_mapping: Dict[str, str], sample_data: Dict[str, List]) -> Dict[str, Any]:
        """Process data based on user requirements"""
        # Interpret user requirements
        instructions = self.llm.interpret_requirements(requirements, schema_mapping, sample_data)
        
        # Load data
        df = read_file(filepath)
        
        # Apply filters if specified
        if "filters" in instructions and instructions["filters"]:
            df = self._apply_filters(df, instructions["filters"])
        
        # Apply groupby and aggregation if specified
        if "groupby" in instructions and instructions["groupby"]:
            df = self._apply_groupby_aggregation(df, instructions)
        
        # Prepare final result
        result = {
            "data": df.to_dict(orient="records"),
            "visualization_info": instructions.get("visualization", {}),
            "processed_columns": list(df.columns),
            "row_count": len(df)
        }
        
        # Add data summary
        result["data_summary"] = self._generate_data_summary(df, instructions)
        
        return result
    
    def _apply_filters(self, df: pd.DataFrame, filters: List[Dict[str, Any]]) -> pd.DataFrame:
        """Apply filters to the dataframe"""
        filtered_df = df.copy()
        
        for filter_obj in filters:
            column = filter_obj.get("column")
            operation = filter_obj.get("operation")
            value = filter_obj.get("value")
            
            if not column or not operation:
                continue
                
            try:
                if operation == "==":
                    filtered_df = filtered_df[filtered_df[column] == value]
                elif operation == "!=":
                    filtered_df = filtered_df[filtered_df[column] != value]
                elif operation == ">":
                    filtered_df = filtered_df[filtered_df[column] > value]
                elif operation == ">=":
                    filtered_df = filtered_df[filtered_df[column] >= value]
                elif operation == "<":
                    filtered_df = filtered_df[filtered_df[column] < value]
                elif operation == "<=":
                    filtered_df = filtered_df[filtered_df[column] <= value]
                elif operation == "in":
                    if isinstance(value, list):
                        filtered_df = filtered_df[filtered_df[column].isin(value)]
                elif operation == "contains":
                    filtered_df = filtered_df[filtered_df[column].str.contains(str(value), na=False)]
            except Exception as e:
                print(f"Error applying filter {filter_obj}: {e}")
        
        return filtered_df
    
    def _apply_groupby_aggregation(self, df: pd.DataFrame, instructions: Dict[str, Any]) -> pd.DataFrame:
        """Apply groupby and aggregation to the dataframe"""
        groupby_cols = instructions.get("groupby", [])
        
        if not groupby_cols:
            return df
            
        try:
            agg_info = instructions.get("aggregation", {})
            agg_method = agg_info.get("method", "sum")
            agg_column = agg_info.get("column", "")
            
            if not agg_column and df.select_dtypes(include=["number"]).columns.any():
                # Use first numeric column as default
                agg_column = df.select_dtypes(include=["number"]).columns[0]
            
            if agg_column:
                if agg_method == "count":
                    grouped_df = df.groupby(groupby_cols).size().reset_index(name="count")
                else:
                    agg_dict = {agg_column: agg_method}
                    grouped_df = df.groupby(groupby_cols).agg(agg_dict).reset_index()
                    # Rename the aggregated column
                    if f"{agg_column}_{agg_method}" in grouped_df.columns:
                        grouped_df.rename(columns={f"{agg_column}_{agg_method}": f"{agg_method}_{agg_column}"}, inplace=True)
                    elif agg_column in grouped_df.columns and not f"{agg_method}_{agg_column}" in grouped_df.columns:
                        grouped_df.rename(columns={agg_column: f"{agg_method}_{agg_column}"}, inplace=True)
                
                return grouped_df
            else:
                return df
        except Exception as e:
            print(f"Error in groupby/aggregation: {e}")
            return df
    
    def _generate_data_summary(self, df: pd.DataFrame, instructions: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the processed data"""
        summary = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns)
        }
        
        # Add numeric column summaries
        numeric_cols = df.select_dtypes(include=["number"]).columns
        if len(numeric_cols) > 0:
            summary["numeric_summary"] = {}
            for col in numeric_cols:
                summary["numeric_summary"][col] = {
                    "min": float(df[col].min()) if not pd.isna(df[col].min()) else None,
                    "max": float(df[col].max()) if not pd.isna(df[col].max()) else None,
                    "mean": float(df[col].mean()) if not pd.isna(df[col].mean()) else None,
                }
        
        # Add categorical column summaries
        cat_cols = df.select_dtypes(include=["object", "category"]).columns
        if len(cat_cols) > 0:
            summary["categorical_summary"] = {}
            for col in cat_cols:
                value_counts = df[col].value_counts().head(5).to_dict()
                summary["categorical_summary"][col] = {
                    "unique_values": df[col].nunique(),
                    "top_values": {str(k): int(v) for k, v in value_counts.items()}
                }
        
        # Add visualization info
        viz_info = instructions.get("visualization", {})
        if viz_info:
            summary["visualization"] = viz_info
        
        return summary
