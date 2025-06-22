import htmx from 'htmx.org'

htmx.config.defaultSwapStyle = 'outerHTML'
htmx.config.globalViewTransitions = true

// ============================================================================
// THEME MANAGER - Sistema de gestión de temas dinámicos
// ============================================================================

class ThemeManager {
    constructor() {
        this.themes = {
            'slate': { name: 'Default/Core' },
            'sky': { name: 'WelpDesk' },
            'forest': { name: 'Welp Payflow' }
        };
        
        this.currentTheme = 'slate';
        this.debug = false; // Desactivar debug por defecto
        this.init();
    }

    init() {
        // Escuchar cambios de HTMX
        document.addEventListener('htmx:afterSwap', () => {
            this.detectAndApplyTheme();
        });
        
        // Escuchar cambios de navegación
        window.addEventListener('popstate', () => {
            this.detectAndApplyTheme();
        });
        
        // Aplicar tema inicial
        this.detectAndApplyTheme();
    }

    detectAndApplyTheme() {
        const namespace = this.getNamespaceFromPage();
        const theme = this.getThemeFromNamespace(namespace);
        
        if (theme !== this.currentTheme) {
            this.setTheme(theme);
        }
    }

    getNamespaceFromPage() {
        // 1. Prioridad: Desde el body data-namespace
        const bodyNamespace = document.body?.getAttribute('data-namespace');
        if (bodyNamespace && bodyNamespace !== 'None') {
            return bodyNamespace;
        }
        
        // 2. Desde la URL actual
        const path = window.location.pathname;
        
        if (path.startsWith('/welp-payflow/')) {
            return 'welp_payflow';
        } else if (path.startsWith('/welp-desk/')) {
            return 'welp_desk';
        }
        
        return 'core';
    }

    getThemeFromNamespace(namespace) {
        const themeMap = {
            'welp_payflow': 'forest',
            'welp_desk': 'sky',
            'core': 'slate'
        };
        
        return themeMap[namespace] || 'slate';
    }

    setTheme(themeName) {
        if (!this.themes[themeName]) {
            console.warn(`🎨 Tema "${themeName}" no encontrado`);
            return;
        }

        const previousTheme = this.currentTheme;
        this.currentTheme = themeName;
        
        // Aplicar data-theme al documento
        document.documentElement.setAttribute('data-theme', themeName);
        
        // Log para debugging (solo si está habilitado)
        if (this.debug) {
            console.log(`🎨 Tema cambiado: ${previousTheme} → ${themeName}`);
        }
        
        // Disparar evento personalizado
        document.dispatchEvent(new CustomEvent('themeChanged', {
            detail: { 
                theme: themeName,
                themeName: this.themes[themeName].name,
                previousTheme: previousTheme
            }
        }));
    }

    // Métodos públicos
    getCurrentTheme() {
        return this.currentTheme;
    }

    getThemeInfo(themeName) {
        return this.themes[themeName] || null;
    }

    switchTheme(themeName) {
        this.setTheme(themeName);
    }

    enableDebug(enable = true) {
        this.debug = enable;
    }
}

// ============================================================================
// INSTANCIA GLOBAL
// ============================================================================

window.themeManager = new ThemeManager();

// Funciones de utilidad globales
window.setTheme = (themeName) => {
    window.themeManager.switchTheme(themeName);
};

window.getCurrentTheme = () => {
    return window.themeManager.getCurrentTheme();
};

window.getThemeInfo = (themeName) => {
    return window.themeManager.getThemeInfo(themeName);
};

// ============================================================================
// INICIALIZACIÓN
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Disparar evento HTMX loaded
    document.dispatchEvent(new CustomEvent('htmx:loaded', {
        detail: { version: htmx.version }
    }));
    
    // Aplicar tema inicial con delay para asegurar que el DOM esté listo
    setTimeout(() => {
        window.themeManager.detectAndApplyTheme();
    }, 50);
});
