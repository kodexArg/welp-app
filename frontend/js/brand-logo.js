/**
 * Brand Logo Component
 * Core - Interactive effects for brand logo
 * 
 * Cumple con las reglas 20_FRONTEND_STACK y 30_COMPONENT_ARCHITECTURE
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all brand logo components
    const brandLogos = document.querySelectorAll('.brand-logo');
    
    brandLogos.forEach(function(logo) {
        const iconElement = logo.querySelector('.icon-glow');
        if (iconElement) {
            // Hover effects
            logo.addEventListener('mouseenter', function() {
                iconElement.classList.add('hover-effect');
            });
            
            logo.addEventListener('mouseleave', function() {
                iconElement.classList.remove('hover-effect');
            });
        }
    });
    
    // Theme change effects
    document.addEventListener('themeChanged', function(event) {
        const brandIcons = document.querySelectorAll('.brand-icon-main');
        brandIcons.forEach(icon => {
            icon.classList.add('theme-change');
            setTimeout(() => {
                icon.classList.remove('theme-change');
            }, 50);
        });
    });
}); 