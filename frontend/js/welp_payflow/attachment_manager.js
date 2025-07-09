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
            const hasFile = input.files && input.files.length > 0;
            
            // Si es la última fila Y no hemos llegado al máximo, mostrar botón +
            if (index === rows.length - 1 && attachmentCount < maxAttachments) {
                const addButton = document.createElement('button');
                addButton.type = 'button';
                addButton.className = 'button-minimal add-attachment';
                addButton.textContent = '+';
                row.appendChild(addButton);
            }
            
            // Si tiene archivo O no es la primera fila, mostrar botón ×
            if (hasFile || index > 0) {
                const removeButton = document.createElement('button');
                removeButton.type = 'button';
                removeButton.className = 'button-minimal remove-attachment';
                removeButton.textContent = '×';
                row.appendChild(removeButton);
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
        if (e.target.type === 'file') {
            updateButtons();
        }
    });

    // Inicializar botones
    updateButtons();
}); 