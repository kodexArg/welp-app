/**
 * PayFlow Create Form Component
 * Welp Payflow - Form logic for creating payment requests
 * 
 * Cumple con las reglas 20_FRONTEND_STACK y 30_COMPONENT_ARCHITECTURE
 */

import { FORM_CONFIG } from './payflow-config.js';

document.addEventListener('DOMContentLoaded', function() {
    const components = ['component-udn', 'component-sector', 'component-accounting', 'component-fields-body'];
    const fields = {
        udn: document.querySelector('input[name="udn"]'),
        sector: document.querySelector('input[name="sector"]'),
        accounting_category: document.querySelector('input[name="accounting_category"]'),
        title: document.querySelector('input[name="title"]'),
        description: document.querySelector('textarea[name="description"]'),
        estimated_amount: document.querySelector('input[name="estimated_amount"]')
    };
    
    /**
     * Gets field value (supports both traditional fields and treemap components)
     */
    function getFieldValue(fieldName) {
        const field = fields[fieldName];
        if (!field) return '';
        
        const treemapApi = window[`selectField_${fieldName}`];
        if (treemapApi) {
            return treemapApi.getCurrentValue();
        }
        
        return field.value || '';
    }
    
    /**
     * Sets field value (supports both traditional fields and treemap components)
     */
    function setFieldValue(fieldName, value) {
        const field = fields[fieldName];
        if (!field) return;
        
        const treemapApi = window[`selectField_${fieldName}`];
        if (treemapApi) {
            treemapApi.selectValue(value);
        } else {
            field.value = value;
        }
    }
    
    /**
     * Toggles component visibility and enables/disables its form controls
     */
    function toggleComponent(componentId, enable) {
        const component = document.getElementById(componentId);
        if (!component) return;
        
        component.classList.toggle('active', enable);
        component.querySelectorAll('input, textarea, select').forEach(input => {
            input.disabled = !enable;
        });
        
        // Handle treemap components
        const fieldName = componentId.replace('component-', '');
        const treemapApi = window[`selectField_${fieldName}`];
        if (treemapApi) {
            treemapApi.setEnabled(enable);
        }
    }
    
    /**
     * Fetches select field options from the API with optional parameters
     */
    async function loadSelectOptions(fieldType, params = {}) {
        try {
            const baseUrl = document.querySelector('[data-select-options-url]')?.dataset.selectOptionsUrl;
            if (!baseUrl) {
                console.error('Select options URL not found');
                return [];
            }
            
            const url = new URL(baseUrl.replace('FIELD_TYPE', fieldType), window.location.origin);
            Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
            
            const response = await fetch(url);
            const data = await response.json();
            
            if (data.error) {
                console.error('Error loading options:', data.error);
                return [];
            }
            
            return data.options || [];
        } catch (error) {
            console.error('Error fetching options:', error);
            return [];
        }
    }
    
    /**
     * Updates a select field with new option elements (supports both select and treemap)
     */
    function updateSelectField(field, options) {
        if (!field) return;
        
        const fieldName = field.name;
        const treemapApi = window[`selectField_${fieldName}`];
        
        if (treemapApi) {
            // Use treemap component API
            treemapApi.updateOptions(options);
        } else {
            // Fallback to traditional select
            field.innerHTML = '';
            options.forEach(option => {
                const optionElement = document.createElement('option');
                optionElement.value = option.value;
                optionElement.textContent = option.text;
                field.appendChild(optionElement);
            });
        }
    }
    
    /**
     * Handles UDN field changes and updates dependent sector options
     */
    async function handleUdnChange() {
        const udnValue = getFieldValue('udn');
        
        if (udnValue) {
            const sectorOptions = await loadSelectOptions('sector', { udn_id: udnValue });
            updateSelectField(fields.sector, sectorOptions);
        } else {
            updateSelectField(fields.sector, [{ value: '', text: '--- Seleccionar Sector ---' }]);
        }
        
        setFieldValue('sector', '');
        setFieldValue('accounting_category', '');
        
        evaluateComponents();
    }
    
    /**
     * Handles sector field changes and triggers component evaluation
     */
    async function handleSectorChange() {
        evaluateComponents();
    }
    
    /**
     * Evaluates which form components should be active based on field values
     */
    function evaluateComponents() {
        let activeIndex = -1;
        
        if (getFieldValue('udn')) {
            activeIndex = 0;
            if (getFieldValue('sector')) {
                activeIndex = 1;
                if (getFieldValue('accounting_category')) {
                    activeIndex = 2;
                }
            }
        }
        
        components.forEach((id, index) => {
            toggleComponent(id, index <= activeIndex + 1);
        });
    }
    
    /**
     * Checks if all required fields are filled and enables/disables submit button
     */
    function checkSubmitButton() {
        const required = [
            getFieldValue('udn'),
            getFieldValue('sector'), 
            getFieldValue('accounting_category'),
            fields.title?.value.trim(), 
            fields.description?.value.trim()
        ];
        
        const submitButton = document.getElementById('submit-button');
        if (submitButton) {
            submitButton.disabled = !required.every(Boolean);
        }
    }
    
    /**
     * Clears all form fields and resets to initial state
     */
    async function clearForm() {
        // Clear all fields using the unified approach
        Object.keys(fields).forEach(fieldName => {
            const field = fields[fieldName];
            if (!field) return;
            
            // Use setFieldValue for select fields (udn, sector, accounting_category)
            if (['udn', 'sector', 'accounting_category'].includes(fieldName)) {
                setFieldValue(fieldName, '');
            } else {
                // Traditional fields (title, description, estimated_amount)
                field.value = '';
            }
        });
        
        await loadInitialOptions();
        
        components.forEach(id => toggleComponent(id, false));
        toggleComponent(components[0], true);
        checkSubmitButton();
    }
    
    /**
     * Loads initial options for all select fields from the API
     */
    async function loadInitialOptions() {
        // Show loading states for treemap components
        ['udn', 'sector', 'accounting_category'].forEach(fieldName => {
            const treemapApi = window[`selectField_${fieldName}`];
            if (treemapApi) {
                treemapApi.showLoading();
            }
        });
        
        try {
            const udnOptions = await loadSelectOptions('udn');
            updateSelectField(fields.udn, udnOptions);
            
            updateSelectField(fields.sector, [{ value: '', text: '--- Seleccionar Sector ---' }]);
            
            const accountingOptions = await loadSelectOptions('accounting');
            updateSelectField(fields.accounting_category, accountingOptions);
        } catch (error) {
            console.error('Error loading initial options:', error);
        }
    }
    
    /**
     * Waits for treemap components to be ready
     */
    function waitForTreemapComponents() {
        return new Promise((resolve) => {
            let attempts = 0;
            
            const checkInterval = setInterval(() => {
                attempts++;
                const treemapApis = ['udn', 'sector', 'accounting_category'].map(name => 
                    window[`selectField_${name}`]
                );
                
                if (treemapApis.every(api => api !== undefined)) {
                    clearInterval(checkInterval);
                    resolve();
                } else if (attempts >= FORM_CONFIG.TREEMAP_MAX_ATTEMPTS) {
                    console.warn('Timeout waiting for treemap components, proceeding anyway');
                    clearInterval(checkInterval);
                    resolve();
                }
            }, FORM_CONFIG.TREEMAP_POLL_INTERVAL_MS);
        });
    }
    
    /**
     * Initializes the form with options, event listeners, and initial state
     */
    async function initializeForm() {
        // Wait for treemap components to be ready
        await waitForTreemapComponents();
        
        await loadInitialOptions();
        
        // Disable all components first
        components.forEach(id => toggleComponent(id, false));
        
        // Force enable the first component (UDN)
        toggleComponent(components[0], true);
        
        // Set up event listeners
        fields.udn?.addEventListener('change', handleUdnChange);
        fields.sector?.addEventListener('change', handleSectorChange);
        fields.accounting_category?.addEventListener('change', evaluateComponents);
        
        ['title', 'description', 'estimated_amount'].forEach(name => {
            fields[name]?.addEventListener('input', checkSubmitButton);
        });
        
        document.getElementById('clear-button')?.addEventListener('click', clearForm);
        
        evaluateComponents();
        checkSubmitButton();
    }
    
    initializeForm();
}); 