function initNotifications(container) {
    container.querySelectorAll('.notification').forEach(el => {
        const closeBtn = el.querySelector('.notification-close');
        const countdown = el.querySelector('.notification-countdown');
        let time = parseInt(el.dataset.duration || '20');
        const interval = setInterval(() => {
            time--;
            if (countdown) countdown.textContent = time;
            if (time <= 0) {
                clearInterval(interval);
                el.remove();
            }
        }, 1000);
        if (countdown) countdown.textContent = time;
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                clearInterval(interval);
                el.remove();
            });
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('notification-container');
    if (container) {
        initNotifications(container);
        document.addEventListener('htmx:afterSwap', (e) => {
            if (e.target.id === 'notification-container') {
                initNotifications(e.target);
            }
        });
    }
});
