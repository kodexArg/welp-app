document.addEventListener('DOMContentLoaded', () => {
    const countdownEl = document.getElementById('countdown');
    if (!countdownEl) return;

    let seconds = parseInt(countdownEl.dataset.seconds || '10');
    const redirectUrl = countdownEl.dataset.url || '/';
    countdownEl.textContent = seconds;

    const interval = setInterval(() => {
        seconds--;
        countdownEl.textContent = seconds;
        if (seconds <= 0) {
            clearInterval(interval);
            window.location.href = redirectUrl;
        }
    }, 1000);
});
