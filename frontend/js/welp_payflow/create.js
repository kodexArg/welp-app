document.addEventListener('DOMContentLoaded', () => {
    
    const containers = ['udn-container', 'sector-container', 'accounting-category-container', 'fields-body-container'];
    
    function hideFrom(id = 0) {
        containers.forEach((containerId, index) => {
            if (index > id) {
                document.getElementById(containerId).style.display = 'none';
            }
        });
    }
    
    function clearFrom(id = 0) {
        containers.forEach((containerId, index) => {
            if (index >= id) {
                const container = document.getElementById(containerId);
                const radios = container.querySelectorAll('input[type="radio"]');
                radios.forEach(radio => {
                    radio.checked = false;
                });
            }
        });
    }

    function showExact(id = 0) {
        console.log(`Contenedor: ${containers[id]}`);
        document.getElementById(containers[id]).style.display = '';
    }
    
    function showUdn() {
        const udnContainer = document.getElementById('udn-container');
        udnContainer.style.display = '';
        
        const loadUrl = udnContainer.getAttribute('data-url');
        if (loadUrl) {
            fetch(loadUrl)
                .then(response => response.text())
                .then(html => {
                    udnContainer.innerHTML = html;
                });
        }
    }
    
    // Al iniciar: ocultar TODO, limpiar TODO, visibilizar UDN
    hideFrom();
    clearFrom();
    showUdn();
    
    // Al hacer click: detectar contenedor y mostrarlo en messagebox
    document.addEventListener('click', (e) => {
        if (e.target && e.target.matches('input[type="radio"]')) {
            const containerId = e.target.closest('[id$="-container"]')?.id;
            const containerIndex = containers.indexOf(containerId);
            
            clearFrom(containerIndex + 1);
            hideFrom(containerIndex + 1);
            showExact(containerIndex + 1);
        }
    });
    
});
