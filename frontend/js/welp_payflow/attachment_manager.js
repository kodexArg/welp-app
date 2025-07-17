/**
 * Attachment Manager - Gestión de archivos adjuntos en formularios
 * Sigue las reglas: JavaScript mínimo y eficiente sin inline code
 */

document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('attachments-container');
    if (!container) return;
    
    let attachmentCount = 1;
    const maxAttachments = 5;

    // Función para actualizar botones de archivo
    function updateButtons() {
        const rows = container.querySelectorAll('.attachment-input-row');
        
        // Remover todos los botones existentes
        rows.forEach(row => {
            const buttons = row.querySelectorAll('.add-attachment, .remove-attachment');
            buttons.forEach(btn => btn.remove());
        });
        
        rows.forEach((row, index) => {
            const input = row.querySelector('input[type="file"]');
            let fileLabel = row.querySelector('.attachment-file-label');
            if (!fileLabel) {
                fileLabel = document.createElement('span');
                fileLabel.className = 'attachment-file-label text-xs text-earth-400 ml-0 bg-white border border-earth-100 rounded-lg px-3 py-2 w-full block';
                input.insertAdjacentElement('afterend', fileLabel);
                fileLabel.addEventListener('click', function() {
                    input.click();
                });
            }
            if (input.files && input.files.length > 0) {
                fileLabel.textContent = input.files[0].name;
                fileLabel.classList.remove('text-earth-400');
                fileLabel.classList.add('text-earth-700');
                // Mostrar el link de borrar solo si hay archivo seleccionado
                const removeLink = document.createElement('a');
                removeLink.href = '#';
                removeLink.className = 'attachment-action-link remove-attachment';
                removeLink.innerHTML = '<i class="fa fa-trash"></i>Borrar';
                row.appendChild(removeLink);
            } else {
                fileLabel.textContent = 'Seleccionar archivo...';
                fileLabel.classList.remove('text-earth-700');
                fileLabel.classList.add('text-earth-400');
            }
        });
    }

    // Delegación de eventos para botones dinámicos
    container.addEventListener('click', function(e) {
        if (e.target.classList.contains('add-attachment')) {
            e.preventDefault();
            
            if (attachmentCount < maxAttachments) {
                attachmentCount++;
                const newRow = document.createElement('div');
                newRow.className = 'attachment-input-row';
                newRow.innerHTML = `
                    <input 
                        type="file" 
                        name="attachments" 
                        class="form-input attachment-input"
                        accept=".pdf,.doc,.docx,.xls,.xlsx,.png,.jpg,.jpeg,.gif"
                    >
                `;
                container.appendChild(newRow);
                updateButtons();
            }
        }
        
        if (e.target.classList.contains('remove-attachment')) {
            e.preventDefault();
            const rowToRemove = e.target.parentElement;
            
            // No permitir eliminar si es la única fila
            if (container.querySelectorAll('.attachment-input-row').length > 1) {
                rowToRemove.remove();
                attachmentCount--;
                updateButtons();
            }
        }
    });

    // Actualizar botones cuando se selecciona un archivo
    container.addEventListener('change', function(e) {
        if (e.target.type === 'file' && e.target.files && e.target.files.length > 0) {
            // Actualizar botones para mostrar el archivo seleccionado
            updateButtons();
            
            // Si no hemos llegado al máximo, agregar automáticamente una nueva fila
            if (attachmentCount < maxAttachments) {
                attachmentCount++;
                const newRow = document.createElement('div');
                newRow.className = 'attachment-input-row';
                newRow.innerHTML = `
                    <input 
                        type="file" 
                        name="attachments" 
                        class="form-input attachment-input"
                        accept=".pdf,.doc,.docx,.xls,.xlsx,.png,.jpg,.jpeg,.gif"
                    >
                `;
                container.appendChild(newRow);
                updateButtons();
            }
        } else if (e.target.type === 'file') {
            // Si no se seleccionó archivo, solo actualizar botones
            updateButtons();
        }
    });

    // Inicializar botones
    updateButtons();
}); 