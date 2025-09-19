// static/js/script.js
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Language support - would be expanded in a real implementation
    const userLanguage = navigator.language || 'en';
    console.log('User language detected:', userLanguage);
    
    // Accessibility features
    function increaseFontSize() {
        const currentSize = parseFloat(getComputedStyle(document.documentElement).fontSize);
        document.documentElement.style.fontSize = (currentSize + 1) + 'px';
    }
    
    function decreaseFontSize() {
        const currentSize = parseFloat(getComputedStyle(document.documentElement).fontSize);
        document.documentElement.style.fontSize = (currentSize - 1) + 'px';
    }
    
    // Would add more accessibility features in a real implementation
});