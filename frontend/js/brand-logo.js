document.addEventListener('DOMContentLoaded', function() {
    const brandLogos = document.querySelectorAll('.brand-logo');
    
    brandLogos.forEach(function(logo) {
        const iconElement = logo.querySelector('.icon-glow');
        if (iconElement) {
            logo.addEventListener('mouseenter', function() {
                iconElement.classList.add('hover-effect');
            });
            
            logo.addEventListener('mouseleave', function() {
                iconElement.classList.remove('hover-effect');
            });
        }
    });
}); 