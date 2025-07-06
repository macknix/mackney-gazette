/**
 * Mackney Gazette - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Handle newsletter form submission
    const newsletterForms = document.querySelectorAll('.newsletter-signup form');
    newsletterForms.forEach(form => {
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            const emailInput = this.querySelector('input[type="email"]');
            if (emailInput && emailInput.value) {
                alert('Thank you for subscribing with: ' + emailInput.value);
                emailInput.value = '';
            } else {
                alert('Please enter a valid email address.');
            }
        });
    });
    
    // Add responsive behavior for images in article content
    const articleImages = document.querySelectorAll('.article-content img');
    articleImages.forEach(img => {
        img.classList.add('img-fluid');
    });
});
