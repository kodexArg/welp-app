/**
 * Sistema de Múltiples Temas - Basado en el patrón de Simon Swiss
 * Maneja el cambio de temas dinámico con localStorage persistence
 */

class ThemeManager {
    constructor() {
        this.themes = {
            'default': {
                name: 'Abyss',
                description: 'Tema predeterminado cálido',
                icon: '🔥'
            },
            'desk': {
                name: 'Desk',
                description: 'Tema azul para WelpDesk',
                icon: '🌊'
            },
            'payflow': {
                name: 'Payflow',
                description: 'Tema verde para pagos',
                icon: '🌿'
            },
            'dark': {
                name: 'Dark',
                description: 'Tema oscuro',
                icon: '🌙'
            }
        };

        this.currentTheme = this.getCurrentTheme();
        this.init();
    }

    /**
     * Detecta el tema apropiado basado en la URL actual
     */
    detectThemeFromUrl() {
        const currentPath = window.location.pathname;
        
        // Detectar aplicación por URL
        if (currentPath.includes('/payflow/')) {
            return 'payflow';
        }
        
        if (currentPath.includes('/desk/')) {
            return 'desk';
        }
        
        // Si estamos en la aplicación principal (core), volver al tema por defecto
        if (currentPath === '/' || 
            currentPath.includes('/core/') || 
            currentPath.includes('/login/') || 
            currentPath.includes('/logout/') ||
            currentPath.includes('/dashboard/') ||
            currentPath.includes('/dev/')) {
            return 'default';
        }
        
        return null; // No hay tema específico para esta URL
    }

    /**
     * Obtiene el tema actual desde localStorage o detecta el tema de la página
     */
    getCurrentTheme() {
        // Primero intentar detectar por URL
        const urlTheme = this.detectThemeFromUrl();
        if (urlTheme) {
            // Si detectamos un tema por URL, verificar si es diferente al guardado
            const savedTheme = localStorage.getItem('welp-theme');
            if (savedTheme !== urlTheme) {
                // Cambiar al tema apropiado para la aplicación
                return urlTheme;
            }
        }

        // Prioridad: localStorage > data-theme del body > 'default'
        const savedTheme = localStorage.getItem('welp-theme');
        if (savedTheme && this.themes[savedTheme]) {
            return savedTheme;
        }

        // Detectar tema actual del body
        const bodyTheme = document.body.getAttribute('data-theme');
        if (bodyTheme && this.themes[bodyTheme]) {
            return bodyTheme;
        }

        return 'default';
    }

    /**
     * Verifica y aplica el tema apropiado basado en la URL actual
     */
    autoDetectAndApplyTheme() {
        const urlTheme = this.detectThemeFromUrl();
        
        if (urlTheme && urlTheme !== this.currentTheme) {
            console.log(`🎨 Auto-cambio de tema: ${this.currentTheme} → ${urlTheme} (URL: ${window.location.pathname})`);
            this.setTheme(urlTheme);
        }
    }

    /**
     * Aplica un tema específico
     */
    setTheme(themeName) {
        if (!this.themes[themeName]) {
            console.warn(`Tema "${themeName}" no encontrado`);
            return;
        }

        // Aplicar al body
        if (themeName === 'default') {
            document.body.removeAttribute('data-theme');
        } else {
            document.body.setAttribute('data-theme', themeName);
        }

        // Guardar en localStorage
        localStorage.setItem('welp-theme', themeName);
        
        // Actualizar estado
        this.currentTheme = themeName;
        
        // Actualizar UI
        this.updateThemeSelectors();
        
        // Disparar evento personalizado
        document.dispatchEvent(new CustomEvent('theme:changed', {
            detail: { theme: themeName, themeData: this.themes[themeName] }
        }));
    }

    /**
     * Cicla al siguiente tema
     */
    nextTheme() {
        const themeKeys = Object.keys(this.themes);
        const currentIndex = themeKeys.indexOf(this.currentTheme);
        const nextIndex = (currentIndex + 1) % themeKeys.length;
        const nextTheme = themeKeys[nextIndex];
        
        this.setTheme(nextTheme);
    }

    /**
     * Inicializa el sistema de temas
     */
    init() {
        // Aplicar tema guardado al cargar la página
        this.setTheme(this.currentTheme);
        
        // Verificar y aplicar tema automático por URL
        this.autoDetectAndApplyTheme();
        
        // Configurar event listeners
        this.setupEventListeners();
        
        // Inicializar selectores de tema cuando el DOM esté listo
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.initializeThemeSelectors();
            });
        } else {
            this.initializeThemeSelectors();
        }
    }

    /**
     * Configura los event listeners globales
     */
    setupEventListeners() {
        // Shortcut de teclado para cambiar tema (Ctrl+Shift+T)
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.shiftKey && e.key === 'T') {
                e.preventDefault();
                this.nextTheme();
            }
        });

        // Detectar cambios de URL para aplicar tema automático
        // Funciona con navegación HTMX y normal
        window.addEventListener('popstate', () => {
            this.autoDetectAndApplyTheme();
        });

        // Detectar cambios HTMX
        document.addEventListener('htmx:afterRequest', () => {
            this.autoDetectAndApplyTheme();
        });
    }

    /**
     * Inicializa todos los selectores de tema en la página
     */
    initializeThemeSelectors() {
        // Dropdown selectors
        document.querySelectorAll('[data-theme-selector]').forEach(selector => {
            this.initializeDropdownSelector(selector);
        });

        // Toggle buttons
        document.querySelectorAll('[data-theme-toggle]').forEach(button => {
            this.initializeToggleButton(button);
        });

        // Buttons con tema específico
        document.querySelectorAll('[data-theme-button]').forEach(button => {
            this.initializeThemeButton(button);
        });
    }

    /**
     * Inicializa un selector dropdown
     */
    initializeDropdownSelector(selector) {
        // Crear opciones
        const select = selector.querySelector('select');
        if (select) {
            // Limpiar opciones existentes
            select.innerHTML = '';
            
            // Agregar opciones de tema
            Object.entries(this.themes).forEach(([key, theme]) => {
                const option = document.createElement('option');
                option.value = key;
                option.textContent = `${theme.icon} ${theme.name}`;
                option.selected = key === this.currentTheme;
                select.appendChild(option);
            });

            // Event listener
            select.addEventListener('change', (e) => {
                this.setTheme(e.target.value);
            });
        }
    }

    /**
     * Inicializa un botón toggle
     */
    initializeToggleButton(button) {
        this.updateToggleButton(button);
        
        button.addEventListener('click', (e) => {
            e.preventDefault();
            this.nextTheme();
        });
    }

    /**
     * Inicializa un botón para tema específico
     */
    initializeThemeButton(button) {
        const targetTheme = button.getAttribute('data-theme-button');
        
        if (this.themes[targetTheme]) {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                this.setTheme(targetTheme);
            });
        }
    }

    /**
     * Actualiza el estado visual de un botón toggle
     */
    updateToggleButton(button) {
        const currentThemeData = this.themes[this.currentTheme];
        const iconElement = button.querySelector('.theme-icon');
        const textElement = button.querySelector('.theme-text');
        
        if (iconElement) {
            iconElement.textContent = currentThemeData.icon;
        }
        if (textElement) {
            textElement.textContent = currentThemeData.name;
        }
        
        // Actualizar atributo para CSS
        button.setAttribute('data-current-theme', this.currentTheme);
    }

    /**
     * Actualiza todos los selectores de tema en la página
     */
    updateThemeSelectors() {
        // Actualizar dropdowns
        document.querySelectorAll('[data-theme-selector] select').forEach(select => {
            select.value = this.currentTheme;
        });

        // Actualizar toggle buttons
        document.querySelectorAll('[data-theme-toggle]').forEach(button => {
            this.updateToggleButton(button);
        });

        // Actualizar botones de tema específico
        document.querySelectorAll('[data-theme-button]').forEach(button => {
            const targetTheme = button.getAttribute('data-theme-button');
            button.classList.toggle('active', targetTheme === this.currentTheme);
        });
    }
}

// Crear instancia global
window.themeManager = new ThemeManager();

// Exportar para uso en otros módulos
export default window.themeManager; 