document.addEventListener('DOMContentLoaded', function() {
    const creationModalEl = document.getElementById('creationModal');
    const creationModal = new bootstrap.Modal(creationModalEl);

    const modalLabel = document.getElementById('creationModalLabel');
    const modalInput = document.getElementById('modal-input-name');
    const modalSaveButton = document.getElementById('modal-save-button');

    // Mettre le focus sur le champ de saisie lorsque la modale est affichée
    creationModalEl.addEventListener('shown.bs.modal', function () {
        modalInput.focus();
    });

    // Fonction pour ouvrir et configurer la modale
    function openCreationModal(button, isMultiple) {
        const selectElement = button.previousElementSibling;
        const createUrl = selectElement.dataset.createUrl;
        const fieldName = selectElement.name;
        const modelName = button.dataset.modelName;

        // Définir le titre de la modale
        modalLabel.textContent = `Ajouter un.e nouvel.le ${modelName.toLowerCase()}`;

        // Nettoyer le champ de saisie
        modalInput.value = '';

        // Stocker les informations nécessaires sur le bouton "Enregistrer" de la modale
        modalSaveButton.dataset.createUrl = createUrl;
        modalSaveButton.dataset.fieldName = fieldName;
        modalSaveButton.dataset.isMultiple = isMultiple;

        // Afficher la modale
        creationModal.show();
    }

    // Gestion des boutons "Ajouter" pour les champs simples
    document.querySelectorAll('.add-new-btn').forEach(button => {
        button.addEventListener('click', function() {
            openCreationModal(this, 'false');
        });
    });

    // Gestion des boutons "Ajouter" pour les champs multiples
    document.querySelectorAll('.add-new-multiple-btn').forEach(button => {
        button.addEventListener('click', function() {
            openCreationModal(this, 'true');
        });
    });

    // Gestion du clic sur le bouton "Enregistrer" de la modale
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

    // ===== Fonctions AJAX (inchangées par rapport à la version précédente) =====

    function createNewOption(url, name, fieldName) {
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
                const select = document.querySelector(`[name="${fieldName}"]`);
                const option = new Option(data.name, data.id, true, true);
                select.add(option);
                select.dispatchEvent(new Event('change'));
            } else {
                alert(`Erreur : ${data.error}`);
            }
        })
        .catch(error => console.error('Erreur AJAX:', error));
    }

    function createNewMultipleOption(url, name, fieldName) {
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
                const select = document.querySelector(`[name="${fieldName}"]`);
                const option = new Option(data.name, data.id, false, true); // Le 3ème paramètre est defaultSelected, le 4ème est selected
                select.add(option);
                select.dispatchEvent(new Event('change'));
            } else {
                alert(`Erreur : ${data.error}`);
            }
        })
        .catch(error => console.error('Erreur AJAX:', error));
    }


    // ===== Gestion des mots-clés (inchangée) =====
    
    document.querySelectorAll('.keyword-input').forEach(input => {
        let timeout;
        const suggestionsContainer = input.parentElement.querySelector('.keyword-suggestions');
        const suggestionsList = suggestionsContainer.querySelector('ul');
        
        input.addEventListener('input', function() {
            clearTimeout(timeout);
            const value = this.value;
            const lastComma = value.lastIndexOf(',');
            const currentTerm = value.substring(lastComma + 1).trim();
            
            if (currentTerm.length < 2) {
                suggestionsContainer.style.display = 'none';
                return;
            }
            
            timeout = setTimeout(() => {
                fetch(`${this.dataset.autocompleteUrl}?term=${encodeURIComponent(currentTerm)}`)
                    .then(response => response.json())
                    .then(data => {
                        showSuggestions(data.results, suggestionsList, suggestionsContainer, input, currentTerm, lastComma);
                    });
            }, 300);
        });
        
        document.addEventListener('click', function(e) {
            if (!input.parentElement.contains(e.target)) {
                suggestionsContainer.style.display = 'none';
            }
        });

        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                const val = this.value;
                const lastComma = val.lastIndexOf(',');
                const currentTerm = val.substring(lastComma + 1).trim();
                if (currentTerm) {
                    createNewKeyword(this.dataset.createUrl, currentTerm, this);
                }
            }
        });
    });

    function showSuggestions(results, suggestionsList, container, input, currentTerm, lastCommaIndex) {
        suggestionsList.innerHTML = '';
        if (results.length === 0) {
            container.style.display = 'none';
            return;
        }
        results.forEach(result => {
            const li = document.createElement('li');
            li.className = 'list-group-item list-group-item-action';
            li.textContent = result.text;
            li.style.cursor = 'pointer';
            
            li.addEventListener('click', function() {
                const beforeLastComma = input.value.substring(0, lastCommaIndex + 1);
                const newValue = beforeLastComma + (beforeLastComma ? ' ' : '') + result.text + ', ';
                input.value = newValue;
                container.style.display = 'none';
                input.focus();
            });
            suggestionsList.appendChild(li);
        });
        container.style.display = 'block';
    }

    function createNewKeyword(url, name, input) {
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({ name: name })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const val = input.value;
                const lastComma = val.lastIndexOf(',');
                const prefix = lastComma >= 0 ? val.substring(0, lastComma + 1) : '';
                input.value = prefix + (prefix ? ' ' : '') + data.name + ', ';
            } else {
                alert(`Erreur : ${data.error}`);
            }
        })
        .catch(err => console.error(err));
    }
});