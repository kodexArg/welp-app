/**
 * Font Preload Component
 * Core - Handle font preloading to avoid FOUC
 * 
 * Cumple con las reglas 20_FRONTEND_STACK y 30_COMPONENT_ARCHITECTURE
 */

document.addEventListener('DOMContentLoaded', function() {
    // Handle font preload
    const fontPreloads = document.querySelectorAll('.font-preload');
    
    fontPreloads.forEach(function(preload) {
        preload.onload = function() {
            this.onload = null;
            this.rel = 'stylesheet';
        };
    });
}); 