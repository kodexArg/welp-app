/**
 * Logout Component
 * Core - Handle logout form submission
 * 
 * Cumple con las reglas 20_FRONTEND_STACK y 30_COMPONENT_ARCHITECTURE
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize logout functionality
    const logoutLinks = document.querySelectorAll('.logout-link');
    
    logoutLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const logoutForm = document.getElementById('logout-form');
            if (logoutForm) {
                logoutForm.submit();
            }
            
            return false;
        });
    });
}); 