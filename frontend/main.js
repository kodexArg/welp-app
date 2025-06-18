import htmx from 'htmx.org'

htmx.config.defaultSwapStyle = 'outerHTML'
htmx.config.globalViewTransitions = true

document.addEventListener('DOMContentLoaded', function() {
    document.dispatchEvent(new CustomEvent('htmx:loaded', {
        detail: { version: htmx.version }
    }));
});
