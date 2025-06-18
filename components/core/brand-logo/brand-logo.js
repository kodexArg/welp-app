document.addEventListener('DOMContentLoaded', function() {
    const brandLogo = document.querySelector('.brand-logo a');
    
    if (brandLogo) {
        brandLogo.addEventListener('mouseenter', function() {
            const icon = this.querySelector('.icon-glow');
            if (icon) {
                icon.style.filter = 'brightness(1.2)';
            }
        });
        
        brandLogo.addEventListener('mouseleave', function() {
            const icon = this.querySelector('.icon-glow');
            if (icon) {
                icon.style.filter = 'brightness(1)';
            }
        });
    }
}); 