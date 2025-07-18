document.addEventListener('DOMContentLoaded', () => {

    // --- SELECTORES Y ESTADO ---

    // IDs de los contenedores que se cargan dinámicamente.
    // El orden es importante ya que define el flujo del formulario.
    const containerIds = [
        'udn-container',
        'sector-container', 
        'accounting-category-container',
        'fields-body-container'
    ];

    const form = document.getElementById('payflow-form');
    const submitButton = document.getElementById('submit-btn');
    const resetButton = document.getElementById('reset-form-btn');
    const htmxErrorContainer = document.getElementById('htmx-errors');
    const validationErrorContainer = document.getElementById('form-validation-errors');
    const validationErrorList = document.getElementById('validation-error-list');

    // --- FUNCIONES DE MANIPULACIÓN DEL DOM ---

    /**
     * Oculta un contenedor por su índice.
     * @param {number} index - El índice del contenedor en el array `containerIds`.
     */
    function hideContainer(index) {
        const container = document.getElementById(containerIds[index]);
        if (container) {
            container.style.display = 'none';
        }
    }

    /**
     * Oculta todos los contenedores a partir de un índice dado.
     * @param {number} fromIndex - El índice desde el cual empezar a ocultar.
     */
    function hideSubsequentContainers(fromIndex) {
        for (let i = fromIndex; i < containerIds.length; i++) {
            hideContainer(i);
        }
    }
    
    /**
     * Muestra un contenedor por su índice.
     * @param {number} index - El índice del contenedor en el array `containerIds`.
     */
    function showContainer(index) {
        const container = document.getElementById(containerIds[index]);
        if (container) {
            container.style.display = 'block';
        }
    }

    /**
     * Limpia el contenido de un contenedor, desmarcando radios o vaciando inputs.
     * @param {number} index - El índice del contenedor a limpiar.
     */
    function clearContainer(index) {
        const container = document.getElementById(containerIds[index]);
        if (!container) return;

        // Limpia los radio buttons
        container.querySelectorAll('input[type="radio"]').forEach(radio => radio.checked = false);
        
        // Limpia los campos de texto y textarea si es el último contenedor
        if (index === containerIds.length - 1) {
            container.querySelectorAll('input[type="text"], textarea').forEach(input => input.value = '');
        }
    }

    /**
     * Oculta y limpia todos los contenedores a partir de un índice.
     * Se usa al cambiar una selección para reiniciar los pasos siguientes.
     * @param {number} fromIndex - El índice desde el cual empezar.
     */
    function resetSubsequentContainers(fromIndex) {
        for (let i = fromIndex; i < containerIds.length; i++) {
            hideContainer(i);
            clearContainer(i);
        }
    }

    /**
     * Muestra un mensaje de error de validación del formulario.
     * @param {string[]} errors - Un array de mensajes de error.
     */
    function showValidationErrors(errors) {
        validationErrorList.innerHTML = '';
        errors.forEach(error => {
            const li = document.createElement('li');
            li.textContent = error;
            validationErrorList.appendChild(li);
        });
        validationErrorContainer.classList.remove('hidden');
        validationErrorContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    /**
     * Oculta el contenedor de errores de validación.
     */
    function hideValidationErrors() {
        validationErrorContainer.classList.add('hidden');
    }

    /**
     * Reinicia el formulario a su estado inicial.
     */
    function resetForm() {
        // Oculta y limpia todos los contenedores excepto el primero.
        resetSubsequentContainers(1);

        // Oculta los mensajes de error
        if (htmxErrorContainer) htmxErrorContainer.classList.add('hidden');
        hideValidationErrors();
        
        // Carga el primer paso del formulario.
        htmx.ajax('GET', '/payflow/htmx/udn/', '#udn-container');
    }


    // --- LÓGICA DE VALIDACIÓN ---

    /**
     * Valida los campos requeridos del formulario antes del envío.
     * @returns {string[]} - Array con los mensajes de error. Vacío si es válido.
     */
    function validateFormOnSubmit() {
        const errors = [];
        const formData = new FormData(form);

        // Valida que los pasos de selección (UDN, Sector, Categoría) se hayan completado.
        if (!formData.get('udn')) errors.push('La UDN es requerida.');
        if (!formData.get('sector')) errors.push('El Sector es requerido.');
        if (!formData.get('accounting_category')) errors.push('La Categoría Contable es requerida.');

        // Valida los campos de texto que deberían existir en el último paso.
        if (!formData.get('title')?.trim()) errors.push('El Título es requerido.');
        if (!formData.get('description')?.trim()) errors.push('La Descripción es requerida.');

        // Elimina duplicados si los hubiera y devuelve.
        return [...new Set(errors)];
    }


    // --- MANEJADORES DE EVENTOS ---

    // 1. Envío del formulario
    submitButton.addEventListener('click', (e) => {
        e.preventDefault(); // Previene el envío nativo para validar primero.

        const validationErrors = validateFormOnSubmit();
        if (validationErrors.length > 0) {
            showValidationErrors(validationErrors);
            return; // Detiene el proceso si hay errores.
        }

        // Si la validación pasa, oculta errores y envía.
        hideValidationErrors();
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fa fa-spinner fa-spin mr-2" aria-hidden="true"></i>Enviando...';
        
        form.submit();
    });
    
    // 2. Botón de cancelar/reset
    resetButton.addEventListener('click', () => {
        window.location.reload();
    });

    // 3. Cambio en un radio button (selección de UDN, Sector, etc.)
    document.addEventListener('change', (event) => {
        if (event.target.type === 'radio') {
            const radioName = event.target.name;
            const containerId = event.target.closest('[id$="-container"]')?.id;
            
            // Encuentra el índice del contenedor actual.
            const currentIndex = containerIds.indexOf(containerId);
            
            if (currentIndex !== -1) {
                // Reinicia todos los contenedores que le siguen en el flujo.
                // Esto es clave para evitar el `htmx:targetError` al "ir hacia atrás".
                resetSubsequentContainers(currentIndex + 1);
            }
            
            // Oculta errores de validación al cambiar una selección.
            hideValidationErrors();
        }
    });

    // --- MANEJADORES DE EVENTOS HTMX ---

    // Se dispara después de que HTMX ha insertado nuevo contenido en el DOM.
    document.addEventListener('htmx:afterSwap', (event) => {
        // `event.detail.target` es el elemento original que fue el objetivo del swap.
        // `event.target` es el nuevo contenido que se ha insertado.
        const intendedTarget = event.detail.target;
        const newContent = event.target;

        // El problema de `htmx:targetError` ocurre cuando un `hx-swap="outerHTML"`
        // reemplaza un contenedor (ej: <div id="sector-container"></div>) con contenido
        // que NO tiene ese mismo ID. Esto hace que el ID se pierda del DOM.
        // Esta corrección asegura que el ID del contenedor se preserve en el nuevo contenido.
        if (newContent.id !== intendedTarget.id) {
            newContent.id = intendedTarget.id;
        }

        const containerIndex = containerIds.indexOf(intendedTarget.id);

        // Si un contenedor conocido fue actualizado, lo muestra.
        if (containerIndex !== -1) {
            showContainer(containerIndex);
        }
    });

    // Gestiona errores de comunicación de HTMX.
    document.addEventListener('htmx:responseError', () => {
        if (htmxErrorContainer) htmxErrorContainer.classList.remove('hidden');
    });
    
    document.addEventListener('htmx:sendError', () => {
        if (htmxErrorContainer) htmxErrorContainer.classList.remove('hidden');
    });

    document.addEventListener('htmx:beforeRequest', () => {
        if (htmxErrorContainer) htmxErrorContainer.classList.add('hidden');
    });

    // --- INICIALIZACIÓN ---
    resetForm();
});
