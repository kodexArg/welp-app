import htmx from 'htmx.org'

// Configuración de HTMX
htmx.config.defaultSwapStyle = 'outerHTML'
htmx.config.globalViewTransitions = true

// El token CSRF se maneja a través del template tag {% htmx_script %}
// y el atributo hx-headers en el body

// Evento para confirmar que HTMX está cargado
document.addEventListener('DOMContentLoaded', function() {
    document.dispatchEvent(new CustomEvent('htmx:loaded', {
        detail: { version: htmx.version }
    }));
});
