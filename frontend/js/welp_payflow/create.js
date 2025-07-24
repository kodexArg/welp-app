document.addEventListener('DOMContentLoaded', () => {

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

    function hideContainer(index) {
        const container = document.getElementById(containerIds[index]);
        if (container) {
            container.style.display = 'none';
        }
    }

    function hideSubsequentContainers(fromIndex) {
        for (let i = fromIndex; i < containerIds.length; i++) {
            hideContainer(i);
        }
    }
    
    function showContainer(index) {
        const container = document.getElementById(containerIds[index]);
        if (container) {
            container.style.display = 'block';
        }
    }

    function clearContainer(index) {
        const container = document.getElementById(containerIds[index]);
        if (!container) return;

        container.querySelectorAll('input[type="radio"]').forEach(radio => radio.checked = false);
        
        if (index === containerIds.length - 1) {
            container.querySelectorAll('input[type="text"], textarea').forEach(input => input.value = '');
        }
    }

    function resetSubsequentContainers(fromIndex) {
        for (let i = fromIndex; i < containerIds.length; i++) {
            hideContainer(i);
            clearContainer(i);
        }
    }

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

    function hideValidationErrors() {
        validationErrorContainer.classList.add('hidden');
    }

    function resetForm() {
        resetSubsequentContainers(1);
        if (htmxErrorContainer) htmxErrorContainer.classList.add('hidden');
        hideValidationErrors();
        htmx.ajax('GET', '/payflow/htmx/udn/', '#udn-container');
    }

    function validateFormOnSubmit() {
        const errors = [];
        const formData = new FormData(form);

        if (!formData.get('udn')) errors.push('La UDN es requerida.');
        if (!formData.get('sector')) errors.push('El Sector es requerido.');
        if (!formData.get('accounting_category')) errors.push('La Categoría Contable es requerida.');

        if (!formData.get('title')?.trim()) errors.push('El Título es requerido.');
        if (!formData.get('description')?.trim()) errors.push('La Descripción es requerida.');

        return [...new Set(errors)];
    }

    submitButton.addEventListener('click', (e) => {
        e.preventDefault();

        const validationErrors = validateFormOnSubmit();
        if (validationErrors.length > 0) {
            showValidationErrors(validationErrors);
            return;
        }

        hideValidationErrors();
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fa fa-spinner fa-spin mr-2" aria-hidden="true"></i>Enviando...';
        
        form.submit();
    });
    
    resetButton.addEventListener('click', () => {
        window.location.reload();
    });

    document.addEventListener('change', (event) => {
        if (event.target.type === 'radio') {
            const radioName = event.target.name;
            const containerId = event.target.closest('[id$="-container"]')?.id;
            
            const currentIndex = containerIds.indexOf(containerId);
            
            if (currentIndex !== -1) {
                resetSubsequentContainers(currentIndex + 1);
            }
            
            hideValidationErrors();
        }
    });

    document.addEventListener('htmx:afterSwap', (event) => {
        const intendedTarget = event.detail.target;
        const newContent = event.target;

        if (newContent.id !== intendedTarget.id) {
            newContent.id = intendedTarget.id;
        }

        const containerIndex = containerIds.indexOf(intendedTarget.id);

        if (containerIndex !== -1) {
            showContainer(containerIndex);
        }
    });

    document.addEventListener('htmx:responseError', () => {
        if (htmxErrorContainer) htmxErrorContainer.classList.remove('hidden');
    });
    
    document.addEventListener('htmx:sendError', () => {
        if (htmxErrorContainer) htmxErrorContainer.classList.remove('hidden');
    });

    document.addEventListener('htmx:beforeRequest', () => {
        if (htmxErrorContainer) htmxErrorContainer.classList.add('hidden');
    });

    resetForm();
});
