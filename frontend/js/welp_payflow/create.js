document.addEventListener('DOMContentLoaded', () => {
    
    const containers = [
        null, // índice 0 vacío para que coincida con numeración 1-4
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
        console.log('"hideContainers" desde', containers[fromIndex]);
        for (let i = fromIndex; i < containers.length; i++) {
            hideContainer(i);
        }
    }
    
    function showContainer(index) {
        const container = document.getElementById(containers[index]);
        if (container) {
            console.log('"showContainer" >', containers[index]);
            container.style.display = 'block';
        }
    }
    
    function clearContainer(index) {
        const container = document.getElementById(containers[index]);
        if (!container) return;
        
        const radios = container.querySelectorAll('input[type="radio"]');
        radios.forEach(radio => radio.checked = false);
        
        // Limpiar otros inputs (especialmente para fields-body-container)
        if (index === 4) {
            const inputs = container.querySelectorAll('input, textarea');
            inputs.forEach(input => input.value = '');
        }
    }
    
    function clearContainers(fromIndex) {
        console.log('"clearContainers" desde', containers[fromIndex]);
        for (let i = fromIndex; i < containers.length; i++) {
            clearContainer(i);
        }
    }
    
    function resetAll() {
        console.log('resetAll');
        hideContainers(1);
        clearContainers(1);
    }
    
    // Event listener para botón reset
    const resetButton = document.getElementById('reset-form-btn');
    if (resetButton) {
        resetButton.addEventListener('click', function(e) {
            console.log('"resetButton" click');
            e.preventDefault();
            resetAll();
            // Recargar contenido UDN después del reset
            htmx.ajax('GET', '/payflow/htmx/create/udn/', '#udn-container');
        });
    }
    
    // HTMX: mostrar contenedor cuando se carga contenido
    document.addEventListener('htmx:afterSwap', function(event) {
        const targetId = event.target.id;
        let containerIndex = containers.indexOf(targetId);
        
        // Si no se encuentra el contenedor directo, buscar el contenedor padre
        if (containerIndex === -1) {
            const parentContainer = event.target.closest('[id$="-container"]');
            if (parentContainer) {
                containerIndex = containers.indexOf(parentContainer.id);
            }
        }
        
        if (containerIndex !== -1) {
            console.log('"htmx:afterSwap" mostrando', containers[containerIndex]);
            showContainer(containerIndex);
            hideContainers(containerIndex + 1);
            
            // Detectar bypass automático
            const container = document.getElementById(containers[containerIndex]);
            if (container) {
                const autoTrigger = container.querySelector('[hx-trigger="load"]');
                if (autoTrigger) {
                    console.log('BYPASS automático detectado en', containers[containerIndex]);
                }
            }
        }
    });
    
    // Radio buttons: ocultar contenedores siguientes al cambiar selección
    document.addEventListener('change', function(event) {
        if (event.target && event.target.type === 'radio') {
            const containerId = event.target.closest('[id$="-container"]')?.id;
            const containerIndex = containers.indexOf(containerId);
            if (containerIndex !== -1) {
                console.log('"change:radio" en', containers[containerIndex]);
                hideContainers(containerIndex + 1);
            }
        }
    });
    
    // Inicialización
    console.log('Inicialización');
    resetAll();
    
    // Cargar contenido inicial UDN una sola vez
    console.log('Cargando contenido inicial UDN');
    htmx.ajax('GET', '/payflow/htmx/create/udn/', '#udn-container');
});
