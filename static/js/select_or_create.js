/**
 * Dynamic Select-or-Create Widget JavaScript
 * 
 * This module provides interactive functionality for the custom Django widgets
 * that allow users to create new entities on-the-fly without leaving the current form.
 * It handles both single-select and multi-select widgets, as well as keyword/tag
 * input with autocomplete functionality.
 * 
 * Key Features:
 * - Modal-based entity creation for select fields
 * - AJAX communication with Django backend
 * - Real-time keyword autocomplete with suggestions
 * - Automatic form field updates after entity creation
 * - Bootstrap 5 modal integration
 * - CSRF token handling for security
 * 
 * Dependencies:
 * - Bootstrap 5 (for modal functionality)
 * - Django CSRF token (for secure AJAX requests)
 * 
 * Usage:
 * This script is automatically loaded and initialized when the DOM is ready.
 * It works with the custom Django widgets defined in widgets.py:
 * - SelectOrCreateWidget
 * - SelectMultipleOrCreateWidget
 * - TagWidget
 * 
 * @author Aura Development Team
 * @version 1.0
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // ========================================
    // MODAL INITIALIZATION AND SETUP
    // ========================================
    
    // Get modal elements for entity creation
    const creationModalEl = document.getElementById('creationModal');
    const creationModal = new bootstrap.Modal(creationModalEl);
    
    // Get modal components for dynamic content updates
    const modalLabel = document.getElementById('creationModalLabel');
    const modalInput = document.getElementById('modal-input-name');
    const modalSaveButton = document.getElementById('modal-save-button');

    /**
     * Focus on the input field when the modal is displayed
     * This improves user experience by allowing immediate typing
     */
    creationModalEl.addEventListener('shown.bs.modal', function () {
        modalInput.focus();
    });

    // ========================================
    // MODAL CONFIGURATION AND DISPLAY
    // ========================================

    /**
     * Open and configure the creation modal for new entity creation.
     * 
     * This function sets up the modal with appropriate title, clears the input,
     * and stores necessary data for the AJAX request when the user saves.
     * 
     * @param {HTMLElement} button - The "Add new" button that was clicked
     * @param {string} isMultiple - String indicating if this is for multiple selection
     */
    function openCreationModal(button, isMultiple) {
        // Get the associated select element (previous sibling of the button)
        const selectElement = button.previousElementSibling;
        
        // Extract data attributes from the select element and button
        const createUrl = selectElement.dataset.createUrl;  // AJAX endpoint URL
        const fieldName = selectElement.name;               // Form field name
        const modelName = button.dataset.modelName;        // Human-readable model name

        // Configure modal title dynamically based on the entity type
        modalLabel.textContent = `Ajouter un.e nouvel.le ${modelName.toLowerCase()}`;

        // Clear any previous input
        modalInput.value = '';

        // Store necessary information on the save button for later use
        modalSaveButton.dataset.createUrl = createUrl;
        modalSaveButton.dataset.fieldName = fieldName;
        modalSaveButton.dataset.isMultiple = isMultiple;

        // Display the modal
        creationModal.show();
    }

    // ========================================
    // EVENT LISTENERS FOR ADD BUTTONS
    // ========================================

    /**
     * Handle click events for single-select "Add new" buttons
     * These buttons are associated with SelectOrCreateWidget
     */
    document.querySelectorAll('.add-new-btn').forEach(button => {
        button.addEventListener('click', function() {
            openCreationModal(this, 'false');
        });
    });

    /**
     * Handle click events for multi-select "Add new" buttons
     * These buttons are associated with SelectMultipleOrCreateWidget
     */
    document.querySelectorAll('.add-new-multiple-btn').forEach(button => {
        button.addEventListener('click', function() {
            openCreationModal(this, 'true');
        });
    });

    // ========================================
    // MODAL SAVE FUNCTIONALITY
    // ========================================

    /**
     * Handle the modal save button click event
     * Validates input and initiates AJAX request to create new entity
     */
    modalSaveButton.addEventListener('click', function() {
        // Validate input - ensure name is not empty
        const name = modalInput.value.trim();
        if (!name) {
            alert('Le nom ne peut pas être vide.');
            return;
        }

        // Extract stored data from the button's data attributes
        const createUrl = this.dataset.createUrl;
        const fieldName = this.dataset.fieldName;
        const isMultiple = this.dataset.isMultiple === 'true';

        // Call appropriate creation function based on field type
        if (isMultiple) {
            createNewMultipleOption(createUrl, name, fieldName);
        } else {
            createNewOption(createUrl, name, fieldName);
        }

        // Hide the modal after initiating the request
        creationModal.hide();
    });

    // ========================================
    // AJAX ENTITY CREATION FUNCTIONS
    // ========================================

    /**
     * Create a new option for a single-select field via AJAX.
     * 
     * This function sends a POST request to the Django backend to create
     * a new entity, then adds it to the select field and selects it.
     * 
     * @param {string} url - The AJAX endpoint URL for entity creation
     * @param {string} name - The name of the entity to create
     * @param {string} fieldName - The name of the form field to update
     */
    function createNewOption(url, name, fieldName) {
        // Send AJAX request to create new entity
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // Include CSRF token for Django security
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({ name: name })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Get the target select field
                const select = document.querySelector(`[name="${fieldName}"]`);
                
                // Create new option element
                // Parameters: text, value, defaultSelected, selected
                const option = new Option(data.name, data.id, true, true);
                
                // Add the new option to the select field
                select.add(option);
                
                // Trigger change event to notify any listeners
                select.dispatchEvent(new Event('change'));
            } else {
                // Display error message if creation failed
                alert(`Erreur : ${data.error}`);
            }
        })
        .catch(error => {
            console.error('Erreur AJAX:', error);
            alert('Une erreur est survenue lors de la création.');
        });
    }

    /**
     * Create a new option for a multi-select field via AJAX.
     * 
     * Similar to createNewOption but for multiple selection fields.
     * The new option is added and selected, but doesn't become the default.
     * 
     * @param {string} url - The AJAX endpoint URL for entity creation
     * @param {string} name - The name of the entity to create
     * @param {string} fieldName - The name of the form field to update
     */
    function createNewMultipleOption(url, name, fieldName) {
        // Send AJAX request to create new entity
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({ name: name })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Get the target select field
                const select = document.querySelector(`[name="${fieldName}"]`);
                
                // Create new option element
                // Parameters: text, value, defaultSelected, selected
                // For multiple select: defaultSelected=false, selected=true
                const option = new Option(data.name, data.id, false, true);
                
                // Add the new option to the select field
                select.add(option);
                
                // Trigger change event to notify any listeners
                select.dispatchEvent(new Event('change'));
            } else {
                // Display error message if creation failed
                alert(`Erreur : ${data.error}`);
            }
        })
        .catch(error => {
            console.error('Erreur AJAX:', error);
            alert('Une erreur est survenue lors de la création.');
        });
    }

    // No keyword input JS needed when using django-taggit
});