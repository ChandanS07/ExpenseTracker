/**
 * Initialize the application when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize date inputs to today's date
    initializeDateInputs();
    
    // Set up event listeners for sorting
    initializeSorting();
    
    // Set up event listeners for quick date filters
    initializeQuickFilters();
    
    // Set up delete confirmation
    initializeDeleteConfirmation();
    
    // Initialize tooltips
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
});

/**
 * Initialize date inputs with the current date
 */
function initializeDateInputs() {
    const dateInputs = document.querySelectorAll('input[type="date"]:not([data-no-init])');
    const today = new Date().toISOString().split('T')[0];
    
    dateInputs.forEach(input => {
        if (!input.value) {
            input.value = today;
        }
    });
}

/**
 * Initialize sorting for expense tables
 */
function initializeSorting() {
    const sortLinks = document.querySelectorAll('.sort-link');
    
    sortLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const sortBy = this.dataset.sort;
            const currentSortBy = new URLSearchParams(window.location.search).get('sort_by') || 'date';
            const currentSortOrder = new URLSearchParams(window.location.search).get('sort_order') || 'desc';
            
            let newSortOrder = 'asc';
            if (sortBy === currentSortBy && currentSortOrder === 'asc') {
                newSortOrder = 'desc';
            }
            
            // Build the new URL with sorting parameters
            const url = new URL(window.location.href);
            const params = new URLSearchParams(url.search);
            
            params.set('sort_by', sortBy);
            params.set('sort_order', newSortOrder);
            
            url.search = params.toString();
            window.location.href = url.toString();
        });
    });
}

/**
 * Initialize quick date filters
 */
function initializeQuickFilters() {
    const quickFilters = document.querySelectorAll('.quick-filter');
    
    quickFilters.forEach(filter => {
        filter.addEventListener('click', function(e) {
            e.preventDefault();
            
            const period = this.dataset.period;
            let startDate, endDate;
            const today = new Date();
            
            // Calculate start and end dates based on the selected period
            if (period === 'today') {
                startDate = today.toISOString().split('T')[0];
                endDate = startDate;
            } else if (period === 'week') {
                // Start of the current week (Sunday)
                const dayOfWeek = today.getDay();
                const startOfWeek = new Date(today);
                startOfWeek.setDate(today.getDate() - dayOfWeek);
                startDate = startOfWeek.toISOString().split('T')[0];
                
                // End of the week (Saturday)
                endDate = today.toISOString().split('T')[0];
            } else if (period === 'month') {
                // Start of the current month
                const startOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);
                startDate = startOfMonth.toISOString().split('T')[0];
                
                // End of the month (today)
                endDate = today.toISOString().split('T')[0];
            } else if (period === 'year') {
                // Start of the current year
                const startOfYear = new Date(today.getFullYear(), 0, 1);
                startDate = startOfYear.toISOString().split('T')[0];
                
                // End of the year (today)
                endDate = today.toISOString().split('T')[0];
            } else if (period === 'all') {
                startDate = '';
                endDate = '';
            }
            
            // Update the form fields
            const startDateInput = document.getElementById('start_date');
            const endDateInput = document.getElementById('end_date');
            
            if (startDateInput) startDateInput.value = startDate;
            if (endDateInput) endDateInput.value = endDate;
            
            // Submit the form
            const filterForm = document.getElementById('filter-form');
            if (filterForm) filterForm.submit();
        });
    });
}

/**
 * Initialize delete confirmation
 */
function initializeDeleteConfirmation() {
    const deleteButtons = document.querySelectorAll('.delete-expense');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this expense?')) {
                e.preventDefault();
            }
        });
    });
}

/**
 * Format a number as currency (Indian Rupees)
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(amount);
}

/**
 * Validate expense form
 */
function validateExpenseForm() {
    const amountInput = document.getElementById('amount');
    const dateInput = document.getElementById('date');
    const descriptionInput = document.getElementById('description');
    const categoryInput = document.getElementById('category');
    
    let isValid = true;
    
    // Validate amount
    if (!amountInput.value || parseFloat(amountInput.value) <= 0) {
        markInvalid(amountInput, 'Please enter a valid amount greater than zero');
        isValid = false;
    } else {
        markValid(amountInput);
    }
    
    // Validate date
    if (!dateInput.value) {
        markInvalid(dateInput, 'Please select a date');
        isValid = false;
    } else {
        markValid(dateInput);
    }
    
    // Validate description
    if (!descriptionInput.value.trim()) {
        markInvalid(descriptionInput, 'Please enter a description');
        isValid = false;
    } else {
        markValid(descriptionInput);
    }
    
    // Validate category
    if (!categoryInput.value) {
        markInvalid(categoryInput, 'Please select a category');
        isValid = false;
    } else {
        markValid(categoryInput);
    }
    
    return isValid;
}

/**
 * Mark form field as invalid
 */
function markInvalid(element, message) {
    element.classList.add('is-invalid');
    
    // Find or create the feedback element
    let feedback = element.nextElementSibling;
    if (!feedback || !feedback.classList.contains('invalid-feedback')) {
        feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        element.parentNode.insertBefore(feedback, element.nextSibling);
    }
    
    feedback.textContent = message;
}

/**
 * Mark form field as valid
 */
function markValid(element) {
    element.classList.remove('is-invalid');
    element.classList.add('is-valid');
    
    // Remove any existing feedback
    const feedback = element.nextElementSibling;
    if (feedback && feedback.classList.contains('invalid-feedback')) {
        feedback.remove();
    }
}
