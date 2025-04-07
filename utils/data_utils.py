import pandas as pd
import numpy as np
from typing import Dict, List, Any, Union, Optional

def summarize_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate a summary of a dataframe"""
    summary = {
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": list(df.columns),
        "dtypes": {col: str(df[col].dtype) for col in df.columns}
    }
    
    # Add basic statistics for numeric columns
    numeric_cols = df.select_dtypes(include=["number"]).columns
    if len(numeric_cols) > 0:
        summary["numeric_stats"] = df[numeric_cols].describe().to_dict()
    
    # Add information on missing values
    missing_values = df.isnull().sum().to_dict()
    summary["missing_values"] = {k: int(v) for k, v in missing_values.items() if v > 0}
    
    return summary

def safe_convert_to_numeric(df: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
    """Try to convert specified columns (or all) to numeric type"""
    result_df = df.copy()
    
    cols_to_convert = columns if columns is not None else df.columns
    
    for col in cols_to_convert:
        if col in result_df.columns:
            result_df[col] = pd.to_numeric(result_df[col], errors='ignore')
    
    return result_df

def identify_date_columns(df: pd.DataFrame) -> List[str]:
    """Identify columns that likely contain dates"""
    date_cols = []
    
    for col in df.columns:
        # Try to convert to datetime
        try:
            pd.to_datetime(df[col], errors='raise')
            date_cols.append(col)
        except:
            # Check if column name suggests it's a date
            if any(date_term in col.lower() for date_term in ['date', 'time', 'year', 'month', 'day']):
                try:
                    # Try again with some common formats
                    pd.to_datetime(df[col], errors='raise', format='%Y-%m-%d')
                    date_cols.append(col)
                except:
                    pass
    
    return date_cols

def suggest_visualization_type(df: pd.DataFrame, x_col: str, y_col: Optional[str] = None) -> str:
    """Suggest an appropriate visualization type based on column types"""
    # Check if x column exists
    if x_col not in df.columns:
        return "bar"  # Default
    
    x_is_numeric = pd.api.types.is_numeric_dtype(df[x_col])
    x_is_datetime = pd.api.types.is_datetime64_dtype(df[x_col]) or x_col in identify_date_columns(df)
    x_unique_ratio = df[x_col].nunique() / len(df) if len(df) > 0 else 0
    
    # If y_col is provided, use it for additional context
    if y_col and y_col in df.columns:
        y_is_numeric = pd.api.types.is_numeric_dtype(df[y_col])
        
        # Scatter plot for two numeric columns with many unique values
        if x_is_numeric and y_is_numeric and x_unique_ratio > 0.5:
            return "scatter"
        
        # Line chart for datetime x and numeric y
        if x_is_datetime and y_is_numeric:
            return "line"
    
    # Bar chart for categorical x with few unique values
    if not x_is_numeric and df[x_col].nunique() <= 10:
        return "bar"
    
    # Line chart for datetime x
    if x_is_datetime:
        return "line"
    
    # Bar chart for categorical x with moderate unique values
    if not x_is_numeric and df[x_col].nunique() <= 30:
        return "bar"
    
    # Histogram for numeric x
    if x_is_numeric:
        return "histogram"
    
    # Default to bar chart
    return "bar"
