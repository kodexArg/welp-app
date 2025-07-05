
document.addEventListener('DOMContentLoaded', function() {
    const attachmentImages = document.querySelectorAll('.attachment-image');
    
    attachmentImages.forEach(function(image) {
        image.addEventListener('click', function() {
            const url = this.getAttribute('data-url');
            if (url) {
                window.open(url, '_blank');
            }
        });
    });
    
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