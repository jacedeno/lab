// Main JavaScript functionality for SAM.gov Flask App

$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        $('.alert-dismissible').alert('close');
    }, 5000);
    
    // Form validation enhancements
    $('form').on('submit', function() {
        var form = $(this);
        var submitBtn = form.find('button[type="submit"]');
        
        // Add loading state
        if (submitBtn.length) {
            submitBtn.prop('disabled', true);
            var originalText = submitBtn.html();
            submitBtn.data('original-text', originalText);
            submitBtn.html('<i class="fas fa-spinner fa-spin me-2"></i>Processing...');
            
            // Reset button after 30 seconds as fallback
            setTimeout(function() {
                submitBtn.prop('disabled', false);
                submitBtn.html(originalText);
            }, 30000);
        }
    });
    
    // Reset form buttons on page load (in case of back button)
    $('button[type="submit"]').each(function() {
        var btn = $(this);
        btn.prop('disabled', false);
        if (btn.data('original-text')) {
            btn.html(btn.data('original-text'));
        }
    });
    
    // Enhanced form field interactions
    $('.form-control, .form-select').on('focus', function() {
        $(this).closest('.form-group, .mb-3').addClass('focused');
    }).on('blur', function() {
        $(this).closest('.form-group, .mb-3').removeClass('focused');
    });
    
    // Date field validation
    $('input[type="date"]').on('change', function() {
        var dateInput = $(this);
        var dateValue = new Date(dateInput.val());
        var today = new Date();
        
        // Remove time component for comparison
        today.setHours(0, 0, 0, 0);
        
        if (dateValue > today) {
            dateInput.addClass('is-invalid');
            var feedback = dateInput.siblings('.invalid-feedback');
            if (feedback.length === 0) {
                dateInput.after('<div class="invalid-feedback">Date cannot be in the future</div>');
            } else {
                feedback.text('Date cannot be in the future');
            }
        } else {
            dateInput.removeClass('is-invalid');
            dateInput.siblings('.invalid-feedback').remove();
        }
    });
    
    // NAICS code validation
    $('#custom_naics').on('input', function() {
        var value = $(this).val();
        var isValid = /^\d{0,6}$/.test(value);
        
        if (value.length > 0 && !isValid) {
            $(this).addClass('is-invalid');
        } else if (value.length === 6 && isValid) {
            $(this).removeClass('is-invalid').addClass('is-valid');
        } else {
            $(this).removeClass('is-invalid is-valid');
        }
    });
    
    // Smooth scrolling for anchor links
    $('a[href^="#"]').on('click', function(e) {
        var target = $(this.getAttribute('href'));
        if (target.length) {
            e.preventDefault();
            $('html, body').stop().animate({
                scrollTop: target.offset().top - 100
            }, 1000);
        }
    });
    
    // Table enhancements
    if ($('.table-responsive').length) {
        // Add table scroll indicators
        $('.table-responsive').on('scroll', function() {
            var scrollLeft = $(this).scrollLeft();
            var scrollWidth = this.scrollWidth;
            var clientWidth = this.clientWidth;
            
            if (scrollLeft > 0) {
                $(this).addClass('scrolled-left');
            } else {
                $(this).removeClass('scrolled-left');
            }
            
            if (scrollLeft < scrollWidth - clientWidth) {
                $(this).addClass('scrolled-right');
            } else {
                $(this).removeClass('scrolled-right');
            }
        });
        
        // Trigger scroll event on load
        $('.table-responsive').trigger('scroll');
    }
    
    // Search form enhancements
    if ($('#searchForm').length) {
        // Save form state to localStorage
        $('#searchForm input, #searchForm select').on('change', function() {
            var formData = $('#searchForm').serializeArray();
            localStorage.setItem('samgov_search_form', JSON.stringify(formData));
        });
        
        // Restore form state from localStorage
        try {
            var savedFormData = localStorage.getItem('samgov_search_form');
            if (savedFormData) {
                var formData = JSON.parse(savedFormData);
                formData.forEach(function(field) {
                    var element = $('#searchForm [name="' + field.name + '"]');
                    if (element.attr('type') === 'checkbox' || element.attr('type') === 'radio') {
                        element.filter('[value="' + field.value + '"]').prop('checked', true);
                    } else {
                        element.val(field.value);
                    }
                });
            }
        } catch (e) {
            console.log('Could not restore form state:', e);
        }
    }
    
    // Copy to clipboard functionality
    function copyToClipboard(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(function() {
                showToast('Copied to clipboard!', 'success');
            }).catch(function() {
                fallbackCopyToClipboard(text);
            });
        } else {
            fallbackCopyToClipboard(text);
        }
    }
    
    function fallbackCopyToClipboard(text) {
        var textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        try {
            document.execCommand('copy');
            showToast('Copied to clipboard!', 'success');
        } catch (err) {
            showToast('Could not copy to clipboard', 'error');
        }
        document.body.removeChild(textArea);
    }
    
    // Toast notification system
    function showToast(message, type) {
        type = type || 'info';
        var alertClass = 'alert-' + (type === 'error' ? 'danger' : type);
        
        var toast = $('<div class="alert ' + alertClass + ' alert-dismissible fade show position-fixed" style="top: 20px; right: 20px; z-index: 9999; min-width: 300px;">' +
            '<i class="fas fa-' + (type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : 'info-circle') + ' me-2"></i>' +
            message +
            '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>' +
            '</div>');
        
        $('body').append(toast);
        
        setTimeout(function() {
            toast.alert('close');
        }, 3000);
    }
    
    // Expose utility functions globally
    window.copyToClipboard = copyToClipboard;
    window.showToast = showToast;
    
    // Keyboard shortcuts
    $(document).on('keydown', function(e) {
        // Ctrl/Cmd + K for search focus
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            var searchInput = $('#title, #org_name').first();
            if (searchInput.length) {
                searchInput.focus();
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            $('.modal.show').modal('hide');
        }
    });
    
    // Performance monitoring
    if (window.performance && window.performance.timing) {
        $(window).on('load', function() {
            setTimeout(function() {
                var timing = window.performance.timing;
                var loadTime = timing.loadEventEnd - timing.navigationStart;
                console.log('Page load time:', loadTime + 'ms');
                
                // Log slow page loads
                if (loadTime > 3000) {
                    console.warn('Slow page load detected:', loadTime + 'ms');
                }
            }, 0);
        });
    }
    
    // Error handling for AJAX requests
    $(document).ajaxError(function(event, xhr, settings, thrownError) {
        console.error('AJAX Error:', {
            url: settings.url,
            status: xhr.status,
            error: thrownError
        });
        
        if (xhr.status === 401) {
            showToast('Session expired. Please log in again.', 'error');
            setTimeout(function() {
                window.location.href = '/login';
            }, 2000);
        } else if (xhr.status >= 500) {
            showToast('Server error occurred. Please try again.', 'error');
        }
    });
    
    // Initialize any additional components
    initializeComponents();
});

// Component initialization function
function initializeComponents() {
    // Initialize any custom components here
    
    // Example: Initialize custom dropdowns
    $('.custom-dropdown').each(function() {
        // Custom dropdown logic
    });
    
    // Example: Initialize data tables if needed
    if (typeof DataTable !== 'undefined' && $('.data-table').length) {
        $('.data-table').DataTable({
            responsive: true,
            pageLength: 25,
            order: [[0, 'desc']]
        });
    }
}

// Utility functions
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    try {
        var date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    } catch (e) {
        return dateString;
    }
}

function formatCurrency(amount) {
    if (!amount || isNaN(amount)) return 'N/A';
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function truncateText(text, maxLength) {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// Export utility functions
window.formatDate = formatDate;
window.formatCurrency = formatCurrency;
window.truncateText = truncateText;
