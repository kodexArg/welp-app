/**
 * Attachment Handler Component
 * Welp Desk - Handle clicks on attachment images and links
 * 
 * Cumple con las reglas 20_FRONTEND_STACK y 30_COMPONENT_ARCHITECTURE
 */

document.addEventListener('DOMContentLoaded', function() {
    // Handle attachment image clicks
    const attachmentImages = document.querySelectorAll('.attachment-image');
    
    attachmentImages.forEach(function(image) {
        image.addEventListener('click', function() {
            const url = this.getAttribute('data-url');
            if (url) {
                window.open(url, '_blank');
            }
        });
    });
    
    // Handle attachment link clicks (if any future ones need JavaScript)
    const attachmentLinks = document.querySelectorAll('.attachment-link');
    
    attachmentLinks.forEach(function(link) {
        link.addEventListener('click', function() {
            const url = this.getAttribute('data-url');
            if (url) {
                window.open(url, '_blank');
            }
        });
    });
}); 