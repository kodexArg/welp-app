import htmx from 'htmx.org'

htmx.config.defaultSwapStyle = 'outerHTML'
htmx.config.globalViewTransitions = true

// ============================================================================
// INICIALIZACIÓN
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Disparar evento HTMX loaded
    document.dispatchEvent(new CustomEvent('htmx:loaded', {
        detail: { version: htmx.version }
    }));
});

// ============================================================================
// COMPONENTES CORE
// ============================================================================

// Importar componentes que se necesitan en todas las páginas
import './js/logout.js'
import './js/dev-content.js'
import './js/theme-selector.js'
