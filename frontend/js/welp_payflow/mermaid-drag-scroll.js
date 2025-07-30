/**
 * Enable horizontal drag scrolling for mermaid diagrams
 * Hides scrollbar while allowing drag-to-scroll functionality
 */
(function() {
    'use strict';

    function initMermaidDragScroll() {
        const containers = document.querySelectorAll('.ticket-mermaid-container');
        
        containers.forEach(container => {
            const mermaidElement = container.querySelector('.mermaid');
            if (!mermaidElement) return;

            let isDragging = false;
            let startX = 0;
            let scrollLeft = 0;

            // Prevent default drag behavior on images
            mermaidElement.addEventListener('dragstart', (e) => {
                e.preventDefault();
            });

            // Mouse events
            container.addEventListener('mousedown', (e) => {
                isDragging = true;
                container.classList.add('active');
                startX = e.pageX - container.offsetLeft;
                scrollLeft = container.scrollLeft;
                container.style.cursor = 'grabbing';
            });

            container.addEventListener('mouseleave', () => {
                isDragging = false;
                container.classList.remove('active');
                container.style.cursor = 'grab';
            });

            container.addEventListener('mouseup', () => {
                isDragging = false;
                container.classList.remove('active');
                container.style.cursor = 'grab';
            });

            container.addEventListener('mousemove', (e) => {
                if (!isDragging) return;
                e.preventDefault();
                const x = e.pageX - container.offsetLeft;
                const walk = (x - startX) * 2; // Multiplier for faster scrolling
                container.scrollLeft = scrollLeft - walk;
            });

            // Touch events for mobile
            let touchStartX = 0;
            let touchScrollLeft = 0;

            container.addEventListener('touchstart', (e) => {
                touchStartX = e.touches[0].pageX;
                touchScrollLeft = container.scrollLeft;
            });

            container.addEventListener('touchmove', (e) => {
                const touchX = e.touches[0].pageX;
                const walk = (touchStartX - touchX) * 2;
                container.scrollLeft = touchScrollLeft + walk;
            });

            // Hide native scrollbar
            container.style.scrollbarWidth = 'none'; // Firefox
            container.style.msOverflowStyle = 'none'; // IE/Edge
            
            // Webkit browsers
            const style = document.createElement('style');
            style.textContent = `
                .ticket-mermaid-container::-webkit-scrollbar {
                    display: none;
                }
            `;
            document.head.appendChild(style);
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initMermaidDragScroll);
    } else {
        initMermaidDragScroll();
    }

    // Re-initialize after HTMX updates
    document.addEventListener('htmx:afterSwap', initMermaidDragScroll);
})();