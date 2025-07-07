document.addEventListener('DOMContentLoaded', () => {
    const sections = ['sector-container', 'accounting-category-container', 'fields-body-container'];

    function resetAfter(id) {
        const startIndex = sections.indexOf(id);
        if (startIndex === -1) return;

        for (let i = startIndex; i < sections.length; i++) {
            const el = document.getElementById(sections[i]);
            if (el) {
                el.innerHTML = '';
                el.style.display = 'none';
            }
        }
    }

    document.addEventListener('click', (e) => {
        if (e.target.matches('input[type="radio"]')) {
            switch (e.target.name) {
                case 'udn':
                    resetAfter('sector-container');
                    break;
                case 'sector':
                    resetAfter('accounting-category-container');
                    break;
                case 'accounting_category':
                    resetAfter('fields-body-container');
                    break;
            }
        }
    });

    const resetBtn = document.getElementById('reset-form-btn');
    if (resetBtn) {
        resetBtn.addEventListener('click', () => window.location.reload());
    }

    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.target.innerHTML.trim() !== '') {
                mutation.target.style.display = '';
            }
        });
    });
    sections.forEach(id => {
        const el = document.getElementById(id);
        if (el) observer.observe(el, { childList: true });
    });
}); 