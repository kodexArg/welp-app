document.addEventListener('DOMContentLoaded', () => {
    
    const containers = [
        null,
        'udn-container',
        'sector-container', 
        'accounting-category-container',
        'fields-body-container'
    ];
    
    // Sistema de logging mejorado
    const logger = {
        info: (message, data = {}) => {
            console.log(`[PAYFLOW-CREATE] ${message}`, data);
        },
        warn: (message, data = {}) => {
            console.warn(`[PAYFLOW-CREATE] ${message}`, data);
        },
        error: (message, error = null) => {
            console.error(`[PAYFLOW-CREATE] ${message}`, error);
        }
    };
    
    // Estado de interacción del usuario
    const userInteraction = {
        hasTriedSubmit: false,
        touchedFields: new Set()
    };
    
    // Manejo de errores mejorado
    const errorHandler = {
        showHTMXError: () => {
            const errorContainer = document.getElementById('htmx-errors');
            if (errorContainer) {
                errorContainer.classList.remove('hidden');
                errorContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        },
        
        hideHTMXError: () => {
            const errorContainer = document.getElementById('htmx-errors');
            if (errorContainer) {
                errorContainer.classList.add('hidden');
            }
        },
        
        showValidationErrors: (errors) => {
            // Solo mostrar si el usuario ya intentó enviar el formulario
            if (!userInteraction.hasTriedSubmit) return;
            
            const errorContainer = document.getElementById('form-validation-errors');
            const errorList = document.getElementById('validation-error-list');
            
            if (errorContainer && errorList) {
                errorList.innerHTML = '';
                errors.forEach(error => {
                    const li = document.createElement('li');
                    li.textContent = error;
                    errorList.appendChild(li);
                });
                errorContainer.classList.remove('hidden');
                errorContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        },
        
        hideValidationErrors: () => {
            const errorContainer = document.getElementById('form-validation-errors');
            if (errorContainer) {
                errorContainer.classList.add('hidden');
            }
        },
        
        showFieldError: (fieldName, message) => {
            // Solo mostrar si el campo ha sido tocado o si ya intentó enviar
            if (!userInteraction.touchedFields.has(fieldName) && !userInteraction.hasTriedSubmit) return;
            
            const field = document.querySelector(`[name="${fieldName}"]`);
            if (!field) return;
            
            // Remover errores previos
            const existingError = field.closest('.form-group').querySelector('.field-error-live');
            if (existingError) existingError.remove();
            
            // Agregar nuevo error
            const errorDiv = document.createElement('div');
            errorDiv.className = 'field-error-live text-red-600 text-sm mt-1';
            errorDiv.textContent = message;
            errorDiv.setAttribute('role', 'alert');
            
            field.parentNode.insertBefore(errorDiv, field.nextSibling);
        },
        
        hideFieldError: (fieldName) => {
            const field = document.querySelector(`[name="${fieldName}"]`);
            if (!field) return;
            
            const existingError = field.closest('.form-group').querySelector('.field-error-live');
            if (existingError) existingError.remove();
        }
    };
    
    function hideContainer(index) {
        const container = document.getElementById(containers[index]);
        if (container) {
            container.style.display = 'none';
            logger.info(`Container ${containers[index]} hidden`);
        }
    }
    
    function hideContainers(fromIndex) {
        for (let i = fromIndex; i < containers.length; i++) {
            hideContainer(i);
        }
    }
    
    function showContainer(index) {
        const container = document.getElementById(containers[index]);
        if (container) {
            container.style.display = 'block';
            logger.info(`Container ${containers[index]} shown`);
        }
    }
    
    function clearContainer(index) {
        const container = document.getElementById(containers[index]);
        if (!container) return;
        
        const radios = container.querySelectorAll('input[type="radio"]');
        radios.forEach(radio => radio.checked = false);
        
        if (index === 4) {
            const inputs = container.querySelectorAll('input, textarea');
            inputs.forEach(input => input.value = '');
        }
        logger.info(`Container ${containers[index]} cleared`);
    }
    
    function clearContainers(fromIndex) {
        for (let i = fromIndex; i < containers.length; i++) {
            clearContainer(i);
        }
    }
    
    function resetAll() {
        hideContainers(1);
        clearContainers(1);
        errorHandler.hideHTMXError();
        errorHandler.hideValidationErrors();
        userInteraction.hasTriedSubmit = false;
        userInteraction.touchedFields.clear();
        logger.info('Form reset completed');
    }
    
    function reloadPage() {
        logger.info('Reloading page');
        window.location.reload();
    }
    
    // Validación del formulario - solo errores críticos
    function validateForm() {
        const form = document.getElementById('payflow-form');
        const errors = [];
        
        // Validar campos de radio/hidden
        const stepFields = [
            { name: 'udn', label: 'UDN' },
            { name: 'sector', label: 'Sector' },
            { name: 'accounting_category', label: 'Categoría Contable' },
        ];
        stepFields.forEach(field => {
            const checkedInput = form.querySelector(`input[name="${field.name}"]:checked`);
            const hiddenInput = form.querySelector(`input[type="hidden"][name="${field.name}"]`);
            if (!checkedInput && !hiddenInput) {
                errors.push(`${field.label} es requerido`);
            }
        });

        // Validar campos de texto
        const textFields = [
            { name: 'title', label: 'Título' },
            { name: 'description', label: 'Descripción' }
        ];
        
        textFields.forEach(field => {
            const input = form.querySelector(`[name="${field.name}"]`);
            // El campo puede no existir aún si el último paso no se ha cargado
            if (input && !input.value.trim()) {
                errors.push(`${field.label} es requerido`);
            } else if (!input && (field.name === 'title' || field.name === 'description')) {
                // Si los campos de texto principales no existen, es un error
                errors.push('Por favor complete todos los pasos anteriores.');
            }
        });
        
        return [...new Set(errors)]; // Devuelve errores únicos
    }
    
    // Validación en tiempo real de campo individual
    function validateField(fieldName, value) {
        switch (fieldName) {
            case 'title':
                if (!value.trim()) {
                    return 'El título es obligatorio';
                }
                if (value.length > 255) {
                    return 'Máximo 255 caracteres';
                }
                break;
            case 'description':
                if (!value.trim()) {
                    return 'La descripción es obligatoria';
                }
                if (value.length < 10) {
                    return 'Mínimo 10 caracteres';
                }
                break;
            case 'estimated_amount':
                if (value && (isNaN(value) || parseFloat(value) < 0)) {
                    return 'Monto no válido';
                }
                break;
        }
        return null;
    }
    
    // Reset button
    const resetButton = document.getElementById('reset-form-btn');
    if (resetButton) {
        resetButton.addEventListener('click', function(e) {
            e.preventDefault();
            logger.info('Reset button clicked');
            reloadPage();
        });
    }
    
    // Submit button con validación
    const submitButton = document.getElementById('submit-btn');
    if (submitButton) {
        const form = document.getElementById('payflow-form');
        submitButton.addEventListener('click', function(e) {
            // Prevenir siempre el envío por defecto para controlarlo manualmente
            e.preventDefault();

            logger.info('Submit button clicked');
            userInteraction.hasTriedSubmit = true;
            
            const validationErrors = validateForm();
            if (validationErrors.length > 0) {
                logger.warn('Form validation failed', { errors: validationErrors });
                errorHandler.showValidationErrors(validationErrors);
                return; // Detener si hay errores, el botón sigue activo
            }
            
            // Ocultar errores anteriores
            errorHandler.hideValidationErrors();
            errorHandler.hideHTMXError();
            
            // Deshabilitar botón para evitar doble envío
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fa fa-spinner fa-spin mr-2" aria-hidden="true"></i>Enviando...';
            
            logger.info('Form validation passed, submitting programmatically');
            
            // Enviar el formulario programáticamente
            form.submit();
        });
    }
    
    // Escuchar cambios en campos para validación en tiempo real
    document.addEventListener('input', function(event) {
        const fieldName = event.target.name;
        if (!fieldName) return;
        
        userInteraction.touchedFields.add(fieldName);
        
        const error = validateField(fieldName, event.target.value);
        if (error) {
            errorHandler.showFieldError(fieldName, error);
        } else {
            errorHandler.hideFieldError(fieldName);
        }
    });
    
    // Eventos HTMX mejorados
    document.addEventListener('htmx:beforeRequest', function(event) {
        logger.info('HTMX request starting', { url: event.detail.xhr.responseURL });
        errorHandler.hideHTMXError();
    });
    
    document.addEventListener('htmx:afterRequest', function(event) {
        const xhr = event.detail.xhr;
        if (xhr.status >= 400) {
            logger.error(`HTMX request failed with status ${xhr.status}`, xhr);
            errorHandler.showHTMXError();
        } else {
            logger.info(`HTMX request completed successfully (${xhr.status})`);
        }
    });
    
    document.addEventListener('htmx:responseError', function(event) {
        logger.error('HTMX response error', event.detail);
        errorHandler.showHTMXError();
    });
    
    document.addEventListener('htmx:sendError', function(event) {
        logger.error('HTMX send error', event.detail);
        errorHandler.showHTMXError();
    });
    
    document.addEventListener('htmx:timeout', function(event) {
        logger.error('HTMX timeout', event.detail);
        errorHandler.showHTMXError();
    });
    
    // Container visibility management
    document.addEventListener('htmx:afterSwap', function(event) {
        const targetId = event.target.id;
        let containerIndex = containers.indexOf(targetId);
        
        if (containerIndex === -1) {
            const parentContainer = event.target.closest('[id$="-container"]');
            if (parentContainer) {
                containerIndex = containers.indexOf(parentContainer.id);
            }
        }
        
        if (containerIndex !== -1) {
            showContainer(containerIndex);
            hideContainers(containerIndex + 1);
            logger.info(`Container swap completed for ${targetId}`);
        }
    });
    
    document.addEventListener('change', function(event) {
        if (event.target && event.target.type === 'radio') {
            const containerId = event.target.closest('[id$="-container"]')?.id;
            const containerIndex = containers.indexOf(containerId);
            if (containerIndex !== -1) {
                hideContainers(containerIndex + 1);
                logger.info(`Radio button changed, hiding containers from ${containerIndex + 1}`);
            }
            
            // Limpiar errores de validación cuando se cambia la selección
            errorHandler.hideValidationErrors();
        }
    });
    
    // Initialize
    logger.info('Payflow create form initialized');
    resetAll();
    htmx.ajax('GET', '/payflow/htmx/udn/', '#udn-container');
});
