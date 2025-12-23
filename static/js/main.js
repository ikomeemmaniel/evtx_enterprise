// Main JavaScript file for EVTX Enterprise

// Document ready function
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Enhance file upload interactions
    enhanceFileUpload();
    
    // Add table row click functionality
    enhanceTableInteractions();
    
    // Add search functionality enhancements
    enhanceSearchFunctionality();
});

// File upload enhancements
function enhanceFileUpload() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    
    if (dropZone && fileInput) {
        // Drag and drop visual feedback
        dropZone.addEventListener('dragover', function(e) {
            e.preventDefault();
            dropZone.classList.add('border-primary', 'bg-light');
        });

        dropZone.addEventListener('dragleave', function(e) {
            e.preventDefault();
            dropZone.classList.remove('border-primary', 'bg-light');
        });

        dropZone.addEventListener('drop', function(e) {
            e.preventDefault();
            dropZone.classList.remove('border-primary', 'bg-light');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileSelection(files[0]);
            }
        });

        // File input change handler
        fileInput.addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                handleFileSelection(e.target.files[0]);
            }
        });
    }
}

// Handle file selection
function handleFileSelection(file) {
    // Check file extension
    if (!file.name.toLowerCase().endsWith('.evtx')) {
        showNotification('Please upload only .evtx files', 'warning');
        return;
    }
    
    // Check file size (50MB limit)
    const maxSize = 50 * 1024 * 1024; // 50MB in bytes
    if (file.size > maxSize) {
        showNotification('File size exceeds 50MB limit', 'danger');
        return;
    }
    
    // Update UI
    updateFileInfo(file);
}

// Update file information display
function updateFileInfo(file) {
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const fileInfo = document.getElementById('fileInfo');
    
    if (fileName && fileSize && fileInfo) {
        fileName.textContent = file.name;
        fileSize.textContent = `(${(file.size / 1024 / 1024).toFixed(2)} MB)`;
        fileInfo.style.display = 'block';
        fileInfo.classList.add('fade-in');
    }
}

// Table interaction enhancements
function enhanceTableInteractions() {
    const tableRows = document.querySelectorAll('tbody tr');
    
    tableRows.forEach(function(row) {
        // Add hover effect
        row.addEventListener('mouseenter', function() {
            this.style.cursor = 'pointer';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.cursor = 'default';
        });
    });
}

// Search functionality enhancements
function enhanceSearchFunctionality() {
    const searchForm = document.getElementById('searchForm');
    
    if (searchForm) {
        const inputs = searchForm.querySelectorAll('input, select');
        
        inputs.forEach(function(input) {
            if (input.type !== 'submit') {
                // Add debounced search on input change
                let searchTimeout;
                input.addEventListener('input', function() {
                    clearTimeout(searchTimeout);
                    searchTimeout = setTimeout(function() {
                        // Optional: Add loading indicator
                        showSearchLoading();
                    }, 300);
                });
            }
        });
    }
}

// Show search loading indicator
function showSearchLoading() {
    // This could show a loading spinner or change cursor
    document.body.style.cursor = 'wait';
    
    // Reset cursor after a short delay
    setTimeout(function() {
        document.body.style.cursor = 'default';
    }, 1000);
}

// Notification system
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(function() {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Format timestamp
function formatTimestamp(timestamp) {
    if (!timestamp) return 'N/A';
    
    const date = new Date(timestamp);
    return date.toLocaleString();
}

// Copy to clipboard function
function copyToClipboard(text, button) {
    navigator.clipboard.writeText(text).then(function() {
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check"></i> Copied!';
        button.classList.add('btn-success');
        button.classList.remove('btn-outline-secondary');
        
        setTimeout(function() {
            button.innerHTML = originalText;
            button.classList.remove('btn-success');
            button.classList.add('btn-outline-secondary');
        }, 2000);
    }).catch(function(err) {
        console.error('Failed to copy: ', err);
        showNotification('Failed to copy to clipboard', 'danger');
    });
}

// Export functions for global use
window.EVTXUtils = {
    showNotification: showNotification,
    formatFileSize: formatFileSize,
    formatTimestamp: formatTimestamp,
    copyToClipboard: copyToClipboard
};

// Handle form submission with loading states
document.addEventListener('submit', function(e) {
    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    
    if (submitBtn && !submitBtn.hasAttribute('data-no-loading')) {
        // Disable button and show loading state
        submitBtn.disabled = true;
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
        
        // Re-enable after 10 seconds (in case of errors)
        setTimeout(function() {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        }, 10000);
    }
});

// Add smooth scrolling
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

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K for search focus
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[type="search"], input[placeholder*="search" i]');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal) {
            const modal = bootstrap.Modal.getInstance(openModal);
            if (modal) {
                modal.hide();
            }
        }
    }
});

// Performance monitoring
if (window.performance && window.performance.timing) {
    window.addEventListener('load', function() {
        const loadTime = window.performance.timing.loadEventEnd - window.performance.timing.navigationStart;
        console.log('Page load time:', loadTime + 'ms');
    });
}
