window.hasContentLoaded = function(button) {
    const targetId = button.dataset.content;
    const container = document.getElementById(targetId);
    const contentArea = container?.querySelector('.dev-content-area');
    return contentArea?.hasAttribute('data-content-loaded') && 
           contentArea.innerHTML.trim() !== '' && 
           !contentArea.innerHTML.includes('loading-content') &&
           !contentArea.innerHTML.includes('error-content');
};

window.toggleDevContent = function(button) {
    const targetId = button.dataset.content;
    const container = document.getElementById(targetId);
    const isVisible = !container.classList.contains('hidden');
    
    if (isVisible) {
        closeDevContent(button, container);
        return;
    }
    
    closeAllDevContainers();
    openDevContent(button, container);
    
    if (!window.hasContentLoaded(button)) {
        const contentArea = container.querySelector('.dev-content-area');
        contentArea.removeAttribute('data-content-loaded');
    }
};

function closeDevContent(button, container) {
    button.classList.remove('active');
    button.setAttribute('aria-expanded', 'false');
    container.classList.remove('expanded');
    
    const contentArea = container.querySelector('.dev-content-area');
    if (contentArea) {
        contentArea.classList.remove('htmx-settling');
    }
    
    container.classList.add('wl-dev-slide-up');
    
    setTimeout(() => {
        container.classList.add('hidden');
        container.classList.remove('wl-dev-slide-up');
    }, 300);
}

function openDevContent(button, container) {
    button.classList.add('active');
    button.setAttribute('aria-expanded', 'true');
    container.classList.remove('hidden');
    container.classList.add('wl-dev-slide-down');
    
    const contentArea = container.querySelector('.dev-content-area');
    if (contentArea && contentArea.hasAttribute('data-content-loaded')) {
        setTimeout(() => {
            contentArea.classList.add('htmx-settling');
        }, 100);
    }
    
    setTimeout(() => {
        container.classList.add('expanded');
        container.classList.remove('wl-dev-slide-down');
        
        const contentArea = container.querySelector('.dev-content-area');
        if (contentArea && contentArea.hasAttribute('data-content-loaded')) {
            contentArea.classList.add('htmx-settling');
        }
    }, 450);
}

function closeAllDevContainers() {
    document.querySelectorAll('.dev-nav-button.active').forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-expanded', 'false');
    });
    document.querySelectorAll('.dev-content-container.expanded').forEach(c => {
        const contentArea = c.querySelector('.dev-content-area');
        if (contentArea) {
            contentArea.classList.remove('htmx-settling');
        }
        
        c.classList.remove('expanded');
        c.classList.add('wl-dev-slide-up');
        setTimeout(() => {
            c.classList.add('hidden');
            c.classList.remove('wl-dev-slide-up');
        }, 300);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('htmx:afterSwap', function(event) {
        const target = event.target;
        
        if (target.classList.contains('wl-dev-htmx-content')) {
            target.setAttribute('data-content-loaded', 'true');
            
            const container = target.closest('.dev-content-container');
            const isExpanding = container && !container.classList.contains('hidden');
            
            if (isExpanding) {
                setTimeout(() => {
                    target.classList.add('htmx-settling');
                    target.classList.add('wl-dev-fade-in');
                    
                    setTimeout(() => {
                        target.classList.remove('wl-dev-fade-in');
                    }, 350);
                }, 150);
            }
        }
    });
    
    document.addEventListener('htmx:beforeRequest', function(event) {
        const target = event.target;
        
        if (target.classList.contains('dev-content-area')) {
            target.innerHTML = '<div class="loading-content"><i class="fa fa-spinner fa-spin mr-2"></i>Cargando...</div>';
        }
    });
    
    document.addEventListener('htmx:responseError', function(event) {
        const target = event.target;
        
        if (target.classList.contains('dev-content-area')) {
            target.innerHTML = '<div class="error-content">Error al cargar el contenido</div>';
        }
    });
}); 