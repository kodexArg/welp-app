document.addEventListener('DOMContentLoaded', () => {
    
    const containers = [
        null,
        'udn-container',
        'sector-container', 
        'accounting-category-container',
        'fields-body-container'
    ];
    
    function hideContainer(index) {
        const container = document.getElementById(containers[index]);
        if (container) {
            container.style.display = 'none';
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
    }
    
    function clearContainers(fromIndex) {
        for (let i = fromIndex; i < containers.length; i++) {
            clearContainer(i);
        }
    }
    
    function resetAll() {
        hideContainers(1);
        clearContainers(1);
    }
    
    // Reset button
    const resetButton = document.getElementById('reset-form-btn');
    if (resetButton) {
        resetButton.addEventListener('click', function(e) {
            e.preventDefault();
            resetAll();
            htmx.ajax('GET', '/payflow/htmx/create/udn/', '#udn-container');
        });
    }
    
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
        }
    });
    
    document.addEventListener('change', function(event) {
        if (event.target && event.target.type === 'radio') {
            const containerId = event.target.closest('[id$="-container"]')?.id;
            const containerIndex = containers.indexOf(containerId);
            if (containerIndex !== -1) {
                hideContainers(containerIndex + 1);
            }
        }
    });
    
    // Initialize
    resetAll();
    htmx.ajax('GET', '/payflow/htmx/create/udn/', '#udn-container');
});
