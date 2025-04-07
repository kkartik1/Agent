import os
import pandas as pd
import uuid
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'csv', 'xls', 'xlsx'}

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, upload_folder):
    """Save the uploaded file to disk and return the path"""
    filename = secure_filename(file.filename)
    
    # Generate a unique filename to avoid conflicts
    unique_filename = f"{uuid.uuid4()}_{filename}"
    
    filepath = os.path.join(upload_folder, unique_filename)
    file.save(filepath)
    
    return filepath

def read_file(filepath):
    """Read a CSV or Excel file into a pandas DataFrame"""
    file_ext = filepath.rsplit('.', 1)[1].lower()
    
    if file_ext == 'csv':
        return pd.read_csv(filepath)
    elif file_ext in ['xls', 'xlsx']:
        return pd.read_excel(filepath)
    else:
        raise ValueError(f"Unsupported file extension: {file_ext}")

def get_file_headers(filepath):
    """Extract column headers from the file"""
    df = read_file(filepath)
    return list(df.columns)
