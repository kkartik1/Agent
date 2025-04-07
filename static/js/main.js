document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    const fileInfoSection = document.getElementById('file-info');
    const requirementsSection = document.getElementById('requirements-section');
    const visualizationSection = document.getElementById('visualization-section');
    const loadingSection = document.getElementById('loading-section');
    const processButton = document.getElementById('process-button');
    const downloadButton = document.getElementById('download-button');
    
    let currentFilePath = null;
    let currentVizId = null;
    
    // Handle file upload
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const fileInput = document.getElementById('data-file');
        if (!fileInput.files[0]) {
            alert('Please select a file to upload');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        
        // Show loading indicator
        loadingSection.classList.remove('hidden');
        
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            loadingSection.classList.add('hidden');
            
            if (data.error) {
                alert('Error: ' + data.error);
                return;
            }
            
            // Store the file path for later use
            currentFilePath = data.file_path;
            
            // Display schema mapping information
            displaySchemaMappings(data.schema_mappings);
            
            // Show requirements input section
            fileInfoSection.classList.remove('hidden');
            requirementsSection.classList.remove('hidden');
        })
        .catch(error => {
            loadingSection.classList.add('hidden');
            alert('Error uploading file: ' + error);
        });
    });
    
    // Handle processing request
    processButton.addEventListener('click', function() {
        const requirements = document.getElementById('requirements').value.trim();
        
        if (!requirements) {
            alert('Please enter your visualization requirements');
            return;
        }
        
        if (!currentFilePath) {
            alert('Please upload a file first');
            return;
        }
        
        // Show loading indicator
        loadingSection.classList.remove('hidden');
        visualizationSection.classList.add('hidden');
        
        fetch('/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                file_path: currentFilePath,
                requirements: requirements
            })
        })
        .then(response => response.json())
        .then(data => {
            loadingSection.classList.add('hidden');
            
            if (data.error) {
                alert('Error: ' + data.error);
                return;
            }
            
            // Store the visualization ID for download
            currentVizId = data.viz_id;
            
            // Display the visualization
            const vizContainer = document.getElementById('visualization-container');
            vizContainer.innerHTML = data.visualization_html;
            
            // Display explanation
            const explanationContainer = document.getElementById('visualization-explanation');
            explanationContainer.innerHTML = `<h3>Explanation</h3><p>${data.explanation}</p>`;
            
            // Show visualization section
            visualizationSection.classList.remove('hidden');
        })
        .catch(error => {
            loadingSection.classList.add('hidden');
            alert('Error processing request: ' + error);
        });
    });
    
    // Handle download
    downloadButton.addEventListener('click', function() {
        if (!currentVizId) {
            alert('No visualization available to download');
            return;
        }
        
        window.location.href = `/download/${currentVizId}`;
    });
    
    // Helper function to display schema mappings
    function displaySchemaMappings(schemaMappings) {
        const mappingsContainer = document.getElementById('column-mappings');
        mappingsContainer.innerHTML = '';
        
        const table = document.createElement('table');
        table.className = 'mapping-table';
        
        // Create header row
        const headerRow = document.createElement('tr');
        ['Technical Column', 'Business Entity'].forEach(headerText => {
            const th = document.createElement('th');
            th.textContent = headerText;
            headerRow.appendChild(th);
        });
        table.appendChild(headerRow);
        
        // Create rows for each mapping
        for (const [technical, business] of Object.entries(schemaMappings)) {
            const row = document.createElement('tr');
            
            const techCell = document.createElement('td');
            techCell.textContent = technical;
            row.appendChild(techCell);
            
            const businessCell = document.createElement('td');
            businessCell.textContent = business;
            row.appendChild(businessCell);
            
            table.appendChild(row);
        }
        
        mappingsContainer.appendChild(table);
    }
});
