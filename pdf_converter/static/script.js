document.addEventListener('DOMContentLoaded', function() {
    // Tab switching functionality
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all buttons and contents
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked button and corresponding content
            btn.classList.add('active');
            const tabId = btn.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });
    
    // File upload display
    const fileUpload = document.getElementById('file_upload');
    const fileList = document.getElementById('file-list');
    
    if (fileUpload) {
        fileUpload.addEventListener('change', function() {
            fileList.innerHTML = '';
            
            if (this.files && this.files.length > 0) {
                for (let i = 0; i < this.files.length; i++) {
                    const fileItem = document.createElement('div');
                    fileItem.className = 'file-item';
                    
                    // Determine icon based on file type
                    let iconClass = 'fa-file';
                    if (this.files[i].type.startsWith('image/')) {
                        iconClass = 'fa-file-image';
                    }
                    
                    fileItem.innerHTML = `
                        <i class="fas ${iconClass}"></i>
                        <span>${this.files[i].name}</span>
                    `;
                    fileList.appendChild(fileItem);
                }
            } else {
                fileList.innerHTML = '<div class="file-item"><i class="fas fa-info-circle"></i><span>No files selected</span></div>';
            }
        });
    }
    
    // Drag and drop functionality
    const fileUploadDisplay = document.querySelector('.file-upload-display');
    
    if (fileUploadDisplay) {
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            fileUploadDisplay.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        // Highlight drop area when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            fileUploadDisplay.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            fileUploadDisplay.addEventListener(eventName, unhighlight, false);
        });
        
        function highlight() {
            fileUploadDisplay.classList.add('highlight');
        }
        
        function unhighlight() {
            fileUploadDisplay.classList.remove('highlight');
        }
        
        // Handle dropped files
        fileUploadDisplay.addEventListener('drop', handleDrop, false);
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length) {
                fileUpload.files = files;
                const event = new Event('change');
                fileUpload.dispatchEvent(event);
            }
        }
    }
});