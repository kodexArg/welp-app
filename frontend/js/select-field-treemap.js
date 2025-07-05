
import { TREEMAP_CONFIG } from './payflow-config.js';

document.addEventListener('DOMContentLoaded', function() {
    const selectFields = document.querySelectorAll('.select-field');
    
    selectFields.forEach(container => {
        const fieldNameMatch = container.id.match(/select-field-(.+)/);
        if (!fieldNameMatch) return;
        
        const fieldName = fieldNameMatch[1];
        initializeSelectField(fieldName);
    });
});

function initializeSelectField(fieldName) {
    const containerId = `select-field-${fieldName}`;
    const treemapId = `treemap-${fieldName}`;
    const hiddenInputId = `id_${fieldName}`;
    
    const container = document.getElementById(containerId);
    const treemapContainer = document.getElementById(treemapId);
    const hiddenInput = document.getElementById(hiddenInputId);
    
    if (!container || !treemapContainer || !hiddenInput) {
        console.warn(`Select field components not found for: ${fieldName}`);
        return;
    }
    
    let currentOptions = [];
    let selectedValue = hiddenInput.value || '';
    
    function createToggleButton(option) {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'treemap-toggle-button';
        
        button.dataset.value = option.value;
        button.textContent = option.text;
        button.title = option.text;
        
        const normalizedText = option.text.normalize('NFD');
        const textLength = normalizedText.length;
        if (textLength <= TREEMAP_CONFIG.SHORT_TEXT_THRESHOLD) {
            button.dataset.short = 'true';
            button.classList.add('short');
        } else if (textLength >= TREEMAP_CONFIG.LONG_TEXT_THRESHOLD) {
            button.dataset.long = 'true';
            button.classList.add('long');
        } else {
            button.dataset.medium = 'true';
            button.classList.add('medium');
        }
        
        if (option.value === selectedValue) {
            button.classList.add('active');
        }
        
        button.addEventListener('click', function() {
            selectOption(option.value);
        });
        
        return button;
    }
    
    function createClearButton() {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'treemap-clear-button';
        
        button.innerHTML = '<i class="fa fa-eraser"></i>';
        button.title = 'LIMPIAR SELECCIÓN';
        button.dataset.value = '';
        
        button.addEventListener('click', function() {
            selectOption('');
        });
        
        return button;
    }
    
    function selectOption(value) {
        selectedValue = value;
        hiddenInput.value = value;
        
        treemapContainer.querySelectorAll('.treemap-toggle-button').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.value === value);
        });
        
        treemapContainer.querySelectorAll('.treemap-clear-button').forEach(btn => {
            btn.classList.toggle('highlighted', value === '');
        });
        
        hiddenInput.dispatchEvent(new Event('change', { bubbles: true }));
    }
    
    function updateTreemap(options) {
        console.log(`Updating ${fieldName} treemap with options:`, options);
        
        currentOptions = options;
        treemapContainer.innerHTML = '';
        
        if (!options || options.length === 0) {
            treemapContainer.innerHTML = '<div class="loading-state">No hay opciones disponibles</div>';
            return;
        }
        
        const sortedOptions = options
            .filter(opt => opt.value !== '') 
            .sort((a, b) => {
                const aLength = a.text.normalize('NFD').length;
                const bLength = b.text.normalize('NFD').length;
                return aLength - bLength;
            });
        
        const clearButton = createClearButton();
        treemapContainer.appendChild(clearButton);
        
        sortedOptions.forEach(option => {
            const button = createToggleButton(option);
            treemapContainer.appendChild(button);
        });
        
        setTimeout(() => {
            balanceTreemapGrid();
        }, TREEMAP_CONFIG.LAYOUT_DELAY_MS);
    }
    
    function balanceTreemapGrid() {
        const toggleButtons = treemapContainer.querySelectorAll('.treemap-toggle-button');
        const containerWidth = treemapContainer.offsetWidth - 32; 
        
        if (!containerWidth || toggleButtons.length === 0) return;
        
        const buttonCount = toggleButtons.length;
        const optimalCols = Math.max(2, Math.min(5, Math.floor(containerWidth / TREEMAP_CONFIG.AVG_BUTTON_WIDTH)));
        
        treemapContainer.style.setProperty('--treemap-cols', optimalCols);
        treemapContainer.style.setProperty('--treemap-min-width', `${Math.floor(containerWidth / optimalCols) - 16}px`);
        
        const shortButtons = Array.from(toggleButtons).filter(btn => btn.dataset.short);
        const mediumButtons = Array.from(toggleButtons).filter(btn => btn.dataset.medium);
        const longButtons = Array.from(toggleButtons).filter(btn => btn.dataset.long);
        
        const optimizedOrder = [];
        const maxLength = Math.max(shortButtons.length, mediumButtons.length, longButtons.length);
        
        for (let i = 0; i < maxLength; i++) {
            if (shortButtons[i]) optimizedOrder.push(shortButtons[i]);
            if (longButtons[i]) optimizedOrder.push(longButtons[i]);
            if (mediumButtons[i]) optimizedOrder.push(mediumButtons[i]);
        }
        
        optimizedOrder.forEach((button, index) => {
            button.style.order = index + TREEMAP_CONFIG.BUTTON_ORDER_OFFSET; 
        });
    }
    
    function setEnabled(enabled) {
        treemapContainer.querySelectorAll('.treemap-toggle-button, .treemap-clear-button').forEach(btn => {
            btn.disabled = !enabled;
        });
        
        if (!enabled) {
            treemapContainer.classList.add('opacity-50');
            container.classList.remove('active');
        } else {
            treemapContainer.classList.remove('opacity-50');
            container.classList.add('active');
        }
    }
    
    function showLoading() {
        treemapContainer.innerHTML = '<div class="loading-state"><i class="fa fa-spinner fa-spin mr-2"></i>Cargando opciones...</div>';
    }
    
    const initialOptionsScript = document.getElementById(`initial-options-${fieldName}`);
    if (initialOptionsScript) {
        try {
            const initialOptions = JSON.parse(initialOptionsScript.textContent);
            updateTreemap(initialOptions);
            
            if (selectedValue) {
                selectOption(selectedValue);
            }
        } catch (error) {
            console.error(`Error parsing initial options for ${fieldName}:`, error);
            showLoading();
        }
    } else {
        showLoading();
    }
    
    window[`selectField_${fieldName}`] = {
        updateOptions: updateTreemap,
        setEnabled: setEnabled,
        showLoading: showLoading,
        selectValue: selectOption,
        getCurrentValue: () => selectedValue
    };
    
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(balanceTreemapGrid, TREEMAP_CONFIG.RESIZE_DEBOUNCE_MS);
    });
    
    console.log(`${fieldName} treemap API initialized`);
} 