/**
 * User Toggle Component - Toggle de usuario con dropdown
 * Sigue las reglas: JavaScript mínimo y eficiente sin inline code
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar toggles de usuario
    initUserToggles();
});

function initUserToggles() {
    const toggleButtons = document.querySelectorAll('[data-toggle="user-dropdown"]');
    
    toggleButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            toggleUserDropdown(this);
        });
    });
    
    // Cerrar dropdowns al hacer clic fuera
    document.addEventListener('click', function(event) {
        toggleButtons.forEach(button => {
            if (!button.contains(event.target)) {
                closeUserDropdown(button);
            }
        });
    });
}

function toggleUserDropdown(button) {
    const dropdown = button.querySelector('.user-toggle-dropdown');
    const chevron = button.querySelector('.user-toggle-chevron');
    
    // Cerrar todos los otros dropdowns
    document.querySelectorAll('.user-toggle-dropdown').forEach(d => {
        if (d !== dropdown) {
            closeUserDropdown(d.parentElement);
        }
    });
    
    // Toggle del dropdown actual
    if (dropdown.style.display === 'none') {
        openUserDropdown(button);
    } else {
        closeUserDropdown(button);
    }
}

function openUserDropdown(button) {
    const dropdown = button.querySelector('.user-toggle-dropdown');
    const chevron = button.querySelector('.user-toggle-chevron');
    
    dropdown.style.display = 'block';
    chevron.classList.add('user-toggle-chevron-rotated');
}

function closeUserDropdown(button) {
    const dropdown = button.querySelector('.user-toggle-dropdown');
    const chevron = button.querySelector('.user-toggle-chevron');
    
    dropdown.style.display = 'none';
    chevron.classList.remove('user-toggle-chevron-rotated');
}
