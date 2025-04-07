from flask import Flask, render_template, request, jsonify, send_file
import os
import pandas as pd
import json
import tempfile
from agents.orchestrator import Orchestrator
from utils.file_handler import save_uploaded_file, allowed_file

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize orchestrator
orchestrator = Orchestrator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filepath = save_uploaded_file(file, app.config['UPLOAD_FOLDER'])
        
        # Process the uploaded file
        result = orchestrator.process_file(filepath)
        
        return jsonify(result)
    
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/process', methods=['POST'])
def process_request():
    data = request.json
    file_path = data.get('file_path')
    requirements = data.get('requirements')
    
    if not file_path or not requirements:
        return jsonify({'error': 'Missing file path or requirements'}), 400
    
    # Process the request through orchestrator
    result = orchestrator.process_request(file_path, requirements)
    
    return jsonify(result)

@app.route('/download/<viz_id>', methods=['GET'])
def download_visualization(viz_id):
    # Generate a downloadable HTML file for the visualization
    viz_html = orchestrator.get_downloadable_html(viz_id)
    
    # Create a temporary file to serve for download
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
    with open(temp_file.name, 'w') as f:
        f.write(viz_html)
    
    return send_file(temp_file.name, as_attachment=True, 
                    download_name=f'visualization_{viz_id}.html')

if __name__ == '__main__':
    app.run(debug=True)
