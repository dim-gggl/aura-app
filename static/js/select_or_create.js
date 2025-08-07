document.addEventListener('DOMContentLoaded', function() {
    const creationModalEl = document.getElementById('creationModal');
    const creationModal = new bootstrap.Modal(creationModalEl);

    const modalLabel = document.getElementById('creationModalLabel');
    const modalInput = document.getElementById('modal-input-name');
    const modalSaveButton = document.getElementById('modal-save-button');

    // Focus on the input field when the modal is displayed
    creationModalEl.addEventListener('shown.bs.modal', function () {
        modalInput.focus();
    });

    // Function to open and configure the modal
    function openCreationModal(button, isMultiple) {
        const selectElement = button.previousElementSibling;
        const createUrl = selectElement.dataset.createUrl;
        const fieldName = selectElement.name;
        const modelName = button.dataset.modelName;

        // Set the title of the modal
        modalLabel.textContent = `Ajouter un.e nouvel.le ${modelName.toLowerCase()}`;

        // Clean the input field
        modalInput.value = '';

        // Store the necessary information on the "Save" button of the modal
        modalSaveButton.dataset.createUrl = createUrl;
        modalSaveButton.dataset.fieldName = fieldName;
        modalSaveButton.dataset.isMultiple = isMultiple;

        // Display the modal
        creationModal.show();
    }

    // Management of the "Add" buttons for simple fields
    document.querySelectorAll('.add-new-btn').forEach(button => {
        button.addEventListener('click', function() {
            openCreationModal(this, 'false');
        });
    });

    // Management of the "Add" buttons for multiple fields
    document.querySelectorAll('.add-new-multiple-btn').forEach(button => {
        button.addEventListener('click', function() {
            openCreationModal(this, 'true');
        });
    });

    // Management of the "Save" button of the modal
    modalSaveButton.addEventListener('click', function() {
        const name = modalInput.value.trim();
        if (!name) {
            alert('Le nom ne peut pas être vide.');
            return;
        }

        const createUrl = this.dataset.createUrl;
        const fieldName = this.dataset.fieldName;
        const isMultiple = this.dataset.isMultiple === 'true';

        if (isMultiple) {
            createNewMultipleOption(createUrl, name, fieldName);
        } else {
            createNewOption(createUrl, name, fieldName);
        }

        creationModal.hide();
    });

    // ===== AJAX functions (unchanged from the previous version) =====

    // Create a new option for a single field
    function createNewOption(url, name, fieldName) {
        // Fetch the new option from the server
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({ name: name })
        })
        // Parse the response as JSON
        .then(response => response.json())
        // If the response is successful, add the new option to the select field
        .then(data => {
            if (data.success) {
                // Get the select field
                const select = document.querySelector(`[name="${fieldName}"]`);
                // Create a new option
                const option = new Option(data.name, data.id, true, true);
                // Add the new option to the select field
                select.add(option);
                // Dispatch a change event to the select field
                select.dispatchEvent(new Event('change'));
            } else {
                // If the response is not successful, show an error message
                alert(`Erreur : ${data.error}`);
            }
        })
        // If there is an error, show an error message
        .catch(error => console.error('Erreur AJAX:', error));
    }

    function createNewMultipleOption(url, name, fieldName) {
        // Fetch the new option from the server
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({ name: name })
        })
        // Parse the response as JSON
        .then(response => response.json())
        // If the response is successful, add the new option to the select field
        .then(data => {
            if (data.success) {
                // Get the select field
                const select = document.querySelector(`[name="${fieldName}"]`);
                // Create a new option
                const option = new Option(data.name, data.id, false, true); // The 3rd parameter is defaultSelected, the 4th is selected
                // Add the new option to the select field
                select.add(option);
                // Dispatch a change event to the select field
                select.dispatchEvent(new Event('change'));
            } else {
                // If the response is not successful, show an error message
                alert(`Erreur : ${data.error}`);
            }
        })
        // If there is an error, show an error message
        .catch(error => console.error('Erreur AJAX:', error));
    }


    // ===== Management of keywords (unchanged) =====
    
    document.querySelectorAll('.keyword-input').forEach(input => {
        // Create a timeout variable
        let timeout;
        // Get the suggestions container
        const suggestionsContainer = input.parentElement.querySelector('.keyword-suggestions');
        // Get the suggestions list
        const suggestionsList = suggestionsContainer.querySelector('ul');
        
        input.addEventListener('input', function() {
            // Clear the timeout
            clearTimeout(timeout);
            // Get the value of the input field
            const value = this.value;
            // Get the last comma index
            const lastComma = value.lastIndexOf(',');
            // Get the current term
            const currentTerm = value.substring(lastComma + 1).trim();
            
            // If the current term is less than 2 characters, hide the suggestions container
            if (currentTerm.length < 2) {
                suggestionsContainer.style.display = 'none';
                return;
            }
            
            // Set a timeout to fetch the suggestions
            timeout = setTimeout(() => {
                // Fetch the suggestions from the server
                fetch(`${this.dataset.autocompleteUrl}?term=${encodeURIComponent(currentTerm)}`)
                    // Parse the response as JSON
                    .then(response => response.json())
                    // If the response is successful, show the suggestions
                    .then(data => {
                        showSuggestions(data.results, suggestionsList, suggestionsContainer, input, currentTerm, lastComma);
                    });
            }, 300);
        });
        
        document.addEventListener('click', function(e) {
            // If the clicked element is not a child of the input field, 
            // hide the suggestions container
            if (!input.parentElement.contains(e.target)) {
                suggestionsContainer.style.display = 'none';
            }
        });

        input.addEventListener('keydown', function(e) {
            // If the key pressed is the Enter key
            if (e.key === 'Enter') {
                // Prevent the default behavior
                e.preventDefault();
                // Get the value of the input field
                const val = this.value;
                const lastComma = val.lastIndexOf(',');
                const currentTerm = val.substring(lastComma + 1).trim();
                // If the current term is not empty, create a new keyword
                if (currentTerm) {
                    createNewKeyword(this.dataset.createUrl, currentTerm, this);
                }
            }
        });
    });

    // Show the suggestions
    function showSuggestions(results, suggestionsList, container, input, currentTerm, lastCommaIndex) {
        // Clear the suggestions list
        suggestionsList.innerHTML = '';
        // If the results are empty, hide the suggestions container
        if (results.length === 0) {
            container.style.display = 'none';
            return;
        }
        // For each result, create a new list item
        results.forEach(result => {
            // Create a new list item
            const li = document.createElement('li');
            // Add the class "list-group-item list-group-item-action" to the list item
            li.className = 'list-group-item list-group-item-action';
            // Set the text content of the list item to the result text
            li.textContent = result.text;
            // Set the cursor to pointer
            li.style.cursor = 'pointer';
            
            li.addEventListener('click', function() {
                // Get the value of the input field before the last comma
                const beforeLastComma = input.value.substring(0, lastCommaIndex + 1);
                // Get the new value
                const newValue = beforeLastComma + (beforeLastComma ? ' ' : '') + result.text + ', ';
                // Set the value of the input field to the new value
                input.value = newValue;
                // Hide the suggestions container
                container.style.display = 'none';
                // Focus on the input field
                input.focus();
            });
            // Add the list item to the suggestions list
            suggestionsList.appendChild(li);
        });
        // Show the suggestions container
        container.style.display = 'block';
    }

    // Create a new keyword
    function createNewKeyword(url, name, input) {
        // Fetch the new keyword from the server
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({ name: name })
        })
        // Parse the response as JSON
        .then(res => res.json())
        // If the response is successful, add the new keyword to the input field
        .then(data => {
            if (data.success) {
                // Get the value of the input field
                const val = input.value;
                const lastComma = val.lastIndexOf(',');
                const prefix = lastComma >= 0 ? val.substring(0, lastComma + 1) : '';
                input.value = prefix + (prefix ? ' ' : '') + data.name + ', ';
            } else {
                // If the response is not successful, show an error message
                alert(`Erreur : ${data.error}`);
            }
        })
        // If there is an error, show an error message
        .catch(err => console.error(err));
    }
});