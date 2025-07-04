/**
 * PayFlow Configuration
 * Welp Payflow - Configuración centralizada para cumplir con reglas 10_DJANGO_CORE
 * 
 * Todas las constantes deben venir de variables de entorno o configuración centralizada
 */

// Configuración de Treemap
export const TREEMAP_CONFIG = {
    // Longitudes de texto para clasificación de botones
    SHORT_TEXT_THRESHOLD: parseInt(import.meta.env.VITE_TREEMAP_SHORT_THRESHOLD || '8'),
    LONG_TEXT_THRESHOLD: parseInt(import.meta.env.VITE_TREEMAP_LONG_THRESHOLD || '20'),
    
    // Tiempos de renderizado y layout
    LAYOUT_DELAY_MS: parseInt(import.meta.env.VITE_TREEMAP_LAYOUT_DELAY || '10'),
    RESIZE_DEBOUNCE_MS: parseInt(import.meta.env.VITE_TREEMAP_RESIZE_DEBOUNCE || '150'),
    
    // Dimensiones de botones
    AVG_BUTTON_WIDTH: parseInt(import.meta.env.VITE_TREEMAP_AVG_BUTTON_WIDTH || '120'),
    MIN_BUTTON_WIDTH: parseInt(import.meta.env.VITE_TREEMAP_MIN_BUTTON_WIDTH || '100'),
    
    // Orden DOM
    BUTTON_ORDER_OFFSET: parseInt(import.meta.env.VITE_TREEMAP_ORDER_OFFSET || '10'),
};

// Configuración de Formularios
export const FORM_CONFIG = {
    // Polling de componentes treemap
    TREEMAP_POLL_INTERVAL_MS: parseInt(import.meta.env.VITE_FORM_POLL_INTERVAL || '50'),
    TREEMAP_MAX_ATTEMPTS: parseInt(import.meta.env.VITE_FORM_MAX_ATTEMPTS || '100'),
    
    // Timeout comentado: 5 segundos = 100 intentos * 50ms
    get TREEMAP_TIMEOUT_MS() {
        return this.TREEMAP_MAX_ATTEMPTS * this.TREEMAP_POLL_INTERVAL_MS;
    }
}; 