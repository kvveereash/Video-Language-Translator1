document.addEventListener('DOMContentLoaded', () => {
    // Get all required elements
    const elements = {
        form: document.getElementById('translationForm'),
        dropZone: document.getElementById('dropZone'),
        videoInput: document.getElementById('videoInput'),
        videoUrl: document.getElementById('videoUrl'),
        processUrlButton: document.getElementById('processUrlButton'),
        videoPreview: document.getElementById('videoPreview'),
        progressArea: document.querySelector('.progress-area'),
        progressBar: document.querySelector('.progress-bar'),
        statusText: document.getElementById('statusText'),
        translateButton: document.getElementById('translateButton'),
        downloadButton: document.getElementById('downloadButton'),
        languageSelect: document.getElementById('languageSelect')
    };

    // Verify all elements exist
    for (const [key, element] of Object.entries(elements)) {
        if (!element) {
            console.error(`Could not find element: ${key}`);
            return;
        }
    }

    let currentTaskId = null;
    let isProcessingUrl = false;

    function enableDownload(taskId) {
        const downloadButton = document.createElement('a');
        downloadButton.id = 'downloadButton';
        downloadButton.href = `/api/download/${taskId}`;
        downloadButton.className = 'btn btn-success mt-3';
        downloadButton.innerHTML = 'Download Translated Video';
        downloadButton.download = ''; // This will preserve the original filename
        
        // Remove any existing download button
        const existingButton = document.getElementById('downloadButton');
        if (existingButton) {
            existingButton.remove();
        }
        
        // Add the new download button after the progress bar
        const progressBar = document.querySelector('.progress');
        progressBar.parentNode.insertBefore(downloadButton, progressBar.nextSibling);
    }

    function updateProgress(status) {
        const progressBar = document.querySelector('.progress-bar');
        if (!progressBar) return;
        
        progressBar.style.width = '50%';
        progressBar.style.backgroundColor = '#007bff';  // Bootstrap primary color
        progressBar.innerHTML = `<span style="color: white; padding: 5px;">${status}</span>`;
        
        // Enable the process buttons while showing progress
        const processUrlButton = document.querySelector('button[onclick="processYouTubeURL()"]');
        const translateButton = document.querySelector('button[onclick="translateVideo()"]');
        if (processUrlButton) processUrlButton.disabled = false;
        if (translateButton) translateButton.disabled = false;
    }

    function showError(message) {
        const progressBar = document.querySelector('.progress-bar');
        if (!progressBar) return;
        
        progressBar.style.backgroundColor = '#dc3545';  // Bootstrap danger color
        progressBar.style.width = '100%';
        progressBar.innerHTML = `<span style="color: white; padding: 5px;">Error: ${message}</span>`;
        
        // Enable the process buttons when showing error
        const processUrlButton = document.querySelector('button[onclick="processYouTubeURL()"]');
        const translateButton = document.querySelector('button[onclick="translateVideo()"]');
        if (processUrlButton) processUrlButton.disabled = false;
        if (translateButton) translateButton.disabled = false;
        
        // Hide download button if it exists
        hideDownloadButton();
    }

    function showSuccess(message) {
        const progressBar = document.querySelector('.progress-bar');
        if (!progressBar) return;
        
        progressBar.style.backgroundColor = '#28a745';  // Bootstrap success color
        progressBar.style.width = '100%';
        progressBar.innerHTML = `<span style="color: white; padding: 5px;">${message}</span>`;
        
        // Enable the process buttons on success
        const processUrlButton = document.querySelector('button[onclick="processYouTubeURL()"]');
        const translateButton = document.querySelector('button[onclick="translateVideo()"]');
        if (processUrlButton) processUrlButton.disabled = false;
        if (translateButton) translateButton.disabled = false;
    }

    function resetUI() {
        elements.progressBar.classList.remove('bg-danger', 'bg-success');
        elements.statusText.classList.remove('text-danger', 'text-success');
        elements.progressBar.style.width = '0%';
        elements.statusText.textContent = '';
        elements.progressArea.style.display = 'none';
        elements.downloadButton.style.display = 'none';
        elements.translateButton.disabled = false;
        elements.processUrlButton.disabled = false;
    }

    // Handle URL processing
    elements.processUrlButton.addEventListener('click', async () => {
        console.log('Process URL button clicked');
        const url = elements.videoUrl.value.trim();
        if (!url) {
            showError('Please enter a valid video URL');
            return;
        }
        console.log('Processing URL:', url);

        try {
            elements.progressArea.style.display = 'block';
            elements.statusText.textContent = 'Processing URL...';
            elements.progressBar.style.width = '25%';
            elements.processUrlButton.disabled = true;
            elements.translateButton.disabled = true;

            console.log('Sending request to /api/youtube');
            const response = await fetch('/api/youtube', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url: url,
                    target_language: elements.languageSelect.value
                })
            });
            console.log('Response status:', response.status);
            console.log('Response headers:', Object.fromEntries(response.headers.entries()));

            let data;
            try {
                data = await response.json();
                console.log('Response data:', data);
            } catch (jsonError) {
                console.error('Error parsing JSON:', jsonError);
                const text = await response.text();
                console.log('Raw response text:', text);
                throw new Error('Failed to parse server response');
            }
            
            if (!response.ok || data.status === 'error') {
                throw new Error(data.message || data.error || 'Failed to process video URL');
            }

            currentTaskId = data.task_id;
            console.log('Starting status check for task:', currentTaskId);
            checkStatus(currentTaskId);
        } catch (error) {
            console.error('Error details:', error);
            showError(error.message || 'Failed to process video URL');
            elements.processUrlButton.disabled = false;
            elements.translateButton.disabled = false;
        }
    });

    // Handle drag and drop
    elements.dropZone.addEventListener('click', () => elements.videoInput.click());
    
    elements.dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        elements.dropZone.style.borderColor = '#007bff';
    });

    elements.dropZone.addEventListener('dragleave', () => {
        elements.dropZone.style.borderColor = '#ccc';
    });

    elements.dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        elements.dropZone.style.borderColor = '#ccc';
        
        if (e.dataTransfer.files.length) {
            elements.videoInput.files = e.dataTransfer.files;
            handleVideoSelection(e.dataTransfer.files[0]);
        }
    });

    // Handle file input change
    elements.videoInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleVideoSelection(e.target.files[0]);
        }
    });

    // Handle video selection
    function handleVideoSelection(file) {
        if (file.type.startsWith('video/')) {
            const url = URL.createObjectURL(file);
            elements.videoPreview.src = url;
            elements.videoPreview.style.display = 'block';
            isProcessingUrl = false;
            resetUI();
        } else {
            showError('Please select a valid video file.');
        }
    }

    // Handle translate button click
    elements.translateButton.addEventListener('click', async (e) => {
        e.preventDefault();
        
        if (isProcessingUrl) {
            return; // URL is already being processed
        }

        const file = elements.videoInput.files[0];
        if (!file) {
            showError('Please select a video file.');
            return;
        }

        resetUI();
        const formData = new FormData();
        formData.append('video', file);
        formData.append('target_language', elements.languageSelect.value);

        elements.translateButton.disabled = true;
        elements.processUrlButton.disabled = true;
        elements.progressArea.style.display = 'block';
        elements.progressBar.style.width = '25%';
        elements.statusText.textContent = 'Uploading video...';

        try {
            // Upload video
            const uploadResponse = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const data = await uploadResponse.json();
            
            if (!uploadResponse.ok || data.status === 'error') {
                throw new Error(data.message || 'Video upload failed');
            }

            currentTaskId = data.task_id;
            checkStatus(currentTaskId);
        } catch (error) {
            console.error('Error:', error);
            showError(error.message);
        }
    });

    // Check translation status
    function checkStatus(taskId) {
        fetch(`/api/status/${taskId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('Status update:', data);  // Debug log
                
                if (data.state === 'SUCCESS') {
                    const result = data.result;
                    console.log('Task result:', result);  // Debug log
                    
                    if (result.status === 'success') {
                        showSuccess('Video processed successfully!');
                        enableDownload(taskId);
                    } else if (result.status === 'info') {
                        showInfo(result.message);
                        hideDownloadButton();
                    } else if (result.status === 'error') {
                        showError(result.message);
                        hideDownloadButton();
                    }
                } else if (data.state === 'PROGRESS') {
                    const status = data.meta ? data.meta.status : 'Processing...';
                    updateProgress(status);
                    setTimeout(() => checkStatus(taskId), 2000);
                } else if (data.state === 'FAILURE') {
                    showError('Task failed: ' + (data.result || 'Unknown error'));
                    hideDownloadButton();
                } else {
                    setTimeout(() => checkStatus(taskId), 2000);
                }
            })
            .catch(error => {
                console.error('Error checking status:', error);
                showError('Error checking task status');
                hideDownloadButton();
            });
    }

    function showInfo(message) {
        const progressBar = document.querySelector('.progress-bar');
        progressBar.style.backgroundColor = '#17a2b8';  // Info color
        progressBar.style.width = '100%';
        progressBar.innerHTML = `<span style="color: white; padding: 5px;">${message}</span>`;
    }

    function hideDownloadButton() {
        const downloadButton = document.getElementById('downloadButton');
        if (downloadButton) {
            downloadButton.remove();
        }
    }

    // Add click handler for download button
    elements.downloadButton.addEventListener('click', async (e) => {
        e.preventDefault();
        try {
            const response = await fetch(elements.downloadButton.href);
            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.error || 'Failed to download video');
            }
            
            // Create a blob from the video data
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            
            // Create a temporary link and click it
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'translated_video.mp4';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            console.error('Error:', error);
            showError(error.message);
        }
    });
}); 