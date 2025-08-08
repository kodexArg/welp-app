import './main.css';
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

