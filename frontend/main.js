import htmx from 'htmx.org'
import mermaid from 'mermaid'

window.mermaid = mermaid;

htmx.config.defaultSwapStyle = 'outerHTML'
htmx.config.globalViewTransitions = true

// ============================================================================
// INICIALIZACIÓN
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    mermaid.initialize({ startOnLoad: true });
    // Disparar evento HTMX loaded
    document.dispatchEvent(new CustomEvent('htmx:loaded', {
        detail: { version: htmx.version }
    }));
});

