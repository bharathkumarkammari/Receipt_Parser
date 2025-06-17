// Costco Receipt Parser JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Get form elements
    const uploadForm = document.getElementById('uploadForm');
    const uploadBtn = document.getElementById('uploadBtn');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const fileInput = document.getElementById('file');

    // Handle form submission
    uploadForm.addEventListener('submit', function(e) {
        // Validate file selection
        if (!fileInput.files.length) {
            e.preventDefault();
            showAlert('Please select a PDF or image file to upload', 'error');
            return;
        }

        // Validate file type
        const file = fileInput.files[0];
        const allowedExtensions = ['.pdf', '.jpg', '.jpeg', '.png'];
        if (!allowedExtensions.some(ext => file.name.toLowerCase().endsWith(ext))) {
            e.preventDefault();
            showAlert('Please select a valid PDF or image file', 'error');
            return;
        }

        // Validate file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
            e.preventDefault();
            showAlert('File size must be less than 10MB', 'error');
            return;
        }

        // Show loading indicator
        showLoading();
    });

    // File input change event
    fileInput.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            // Update button text to show selected file
            const fileName = file.name.length > 20 ? 
                file.name.substring(0, 20) + '...' : 
                file.name;
            uploadBtn.innerHTML = `<i class="fas fa-cloud-upload-alt me-2"></i>Upload "${fileName}"`;
        } else {
            uploadBtn.innerHTML = '<i class="fas fa-cloud-upload-alt me-2"></i>Upload & Parse';
        }
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add tooltips to buttons
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Add copy functionality to item codes
    document.querySelectorAll('.font-monospace').forEach(element => {
        element.style.cursor = 'pointer';
        element.title = 'Click to copy item code';
        
        element.addEventListener('click', function() {
            const text = this.textContent;
            navigator.clipboard.writeText(text).then(() => {
                showTemporaryTooltip(this, 'Copied!');
            }).catch(() => {
                showTemporaryTooltip(this, 'Failed to copy');
            });
        });
    });

    // Search functionality for items
    addSearchFunctionality();
});

function showLoading() {
    const uploadBtn = document.getElementById('uploadBtn');
    const loadingIndicator = document.getElementById('loadingIndicator');
    
    // Disable upload button
    uploadBtn.disabled = true;
    uploadBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Processing...';
    
    // Show loading indicator
    loadingIndicator.classList.remove('d-none');
    loadingIndicator.classList.add('pulse');
}

function showAlert(message, type) {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : 'exclamation-circle'} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at top of container
    const container = document.querySelector('.container');
    const firstRow = container.querySelector('.row');
    const alertContainer = document.createElement('div');
    alertContainer.className = 'row';
    alertContainer.innerHTML = '<div class="col-12"></div>';
    alertContainer.firstElementChild.appendChild(alertDiv);
    
    container.insertBefore(alertContainer, firstRow);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alertDiv);
        bsAlert.close();
    }, 5000);
}

function showTemporaryTooltip(element, message) {
    const tooltip = new bootstrap.Tooltip(element, {
        title: message,
        trigger: 'manual'
    });
    
    tooltip.show();
    
    setTimeout(() => {
        tooltip.dispose();
    }, 1500);
}

function addSearchFunctionality() {
    // Add search input to each accordion panel
    document.querySelectorAll('.accordion-body').forEach(accordionBody => {
        const table = accordionBody.querySelector('table');
        if (table) {
            // Create search input
            const searchContainer = document.createElement('div');
            searchContainer.className = 'mb-3';
            searchContainer.innerHTML = `
                <div class="input-group">
                    <span class="input-group-text">
                        <i class="fas fa-search"></i>
                    </span>
                    <input type="text" class="form-control" placeholder="Search items..." />
                </div>
            `;
            
            // Insert before table
            table.parentNode.insertBefore(searchContainer, table);
            
            // Add search functionality
            const searchInput = searchContainer.querySelector('input');
            searchInput.addEventListener('input', function() {
                const searchTerm = this.value.toLowerCase();
                const rows = table.querySelectorAll('tbody tr');
                
                rows.forEach(row => {
                    const itemCode = row.cells[0].textContent.toLowerCase();
                    const itemName = row.cells[1].textContent.toLowerCase();
                    
                    if (itemCode.includes(searchTerm) || itemName.includes(searchTerm)) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
            });
        }
    });
}

// Utility function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Utility function to format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + U to focus file input
    if ((e.ctrlKey || e.metaKey) && e.key === 'u') {
        e.preventDefault();
        document.getElementById('file').focus();
    }
    
    // Escape to clear file selection
    if (e.key === 'Escape') {
        const fileInput = document.getElementById('file');
        if (fileInput.value) {
            fileInput.value = '';
            const uploadBtn = document.getElementById('uploadBtn');
            uploadBtn.innerHTML = '<i class="fas fa-cloud-upload-alt me-2"></i>Upload & Parse';
        }
    }
});

// Add drag and drop functionality
function addDragAndDrop() {
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('file');
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadForm.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadForm.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        uploadForm.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight() {
        uploadForm.classList.add('border-primary');
    }
    
    function unhighlight() {
        uploadForm.classList.remove('border-primary');
    }
    
    uploadForm.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            fileInput.files = files;
            fileInput.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }
}

// Initialize drag and drop
addDragAndDrop();
