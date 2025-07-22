function calculateImageSize(img) {
    const width = img.naturalWidth;
    const height = img.naturalHeight;
    const fileSizeEl = document.getElementById('file-size');

    fetch(img.src, { method: 'HEAD' })
        .then(response => {
            if (!response.ok) {
                fileSizeEl.textContent = `${width}×${height} px`;
                return;
            }
            const contentLength = response.headers.get('content-length');
            if (contentLength) {
                const size = parseInt(contentLength, 10);
                if (size < 1024) fileSizeEl.textContent = `${size} B`;
                else if (size < 1024 * 1024) fileSizeEl.textContent = `${(size / 1024).toFixed(1)} KB`;
                else fileSizeEl.textContent = `${(size / (1024 * 1024)).toFixed(1)} MB`;
            } else {
                fileSizeEl.textContent = `${width}×${height} px`;
            }
        })
        .catch(() => {
            fileSizeEl.textContent = `${width}×${height} px`;
        });
}

// Asignar a window para acceso global desde el `onload` del <img>
window.calculateImageSize = calculateImageSize;

document.addEventListener('DOMContentLoaded', () => {
    const imgElement = document.querySelector('.attachment-image');
    if (imgElement && imgElement.complete) {
        calculateImageSize(imgElement);
    }

    const fileSizeEl = document.getElementById('file-size');
    if (fileSizeEl && fileSizeEl.textContent === 'Calculando...') {
        const openBtn = document.querySelector('.attachment-open-btn');
        if (openBtn) {
            fetch(openBtn.href, { method: 'HEAD' })
                .then(response => {
                    if (!response.ok) {
                        fileSizeEl.textContent = 'Desconocido';
                        return;
                    }
                    const contentLength = response.headers.get('content-length');
                    if (contentLength) {
                        const size = parseInt(contentLength, 10);
                        if (size < 1024) fileSizeEl.textContent = `${size} B`;
                        else if (size < 1024 * 1024) fileSizeEl.textContent = `${(size / 1024).toFixed(1)} KB`;
                        else fileSizeEl.textContent = `${(size / (1024 * 1024)).toFixed(1)} MB`;
                    } else {
                        fileSizeEl.textContent = 'Desconocido';
                    }
                })
                .catch(() => {
                    fileSizeEl.textContent = 'Desconocido';
                });
        }
    }
}); 