document.addEventListener('DOMContentLoaded', function() {
    // Gestion des boutons "Ajouter" pour champs simples
    document.querySelectorAll('.add-new-btn').forEach(button => {
        button.addEventListener('click', function() {
            const fieldName = this.dataset.fieldName;
            const modelName = this.dataset.modelName;
            const createUrl = this.previousElementSibling.dataset.createUrl;
            
            let message = "";
            switch (modelName) {
                case "Artist":
                    message = "Entrez le nom complet du nouvel artiste : ";
                    break;
                case "ArtType":
                    message = "Entrez le nom du nouveau type d'Art : ";
                    break;
                case "Support":
                    message = "Entrez le nom du nouveau matériau à ajouter aux supports : ";
                    break;
                case "Technique":
                    message = "Entrez le nom de la technique à ajouter à la liste : ";
                    break;
                case "Collection":
                    message = "Entrez le nom de la Collection à créer : ";
                    break;
                case "Exhibition":
                    message = "Entrez le nom de la nouvelle expo à ajouter : ";
                    break;
                default:
                    message = `Entrez le nom de la nouvelle entrée pour: ${modelName} :`;
            }
            const name = prompt(message);
            if (name && name.trim()) {
                createNewOption(createUrl, name.trim(), fieldName);
            }
        });
    });
    
    // Gestion des boutons "Ajouter" pour champs multiples (comme les artistes)
    document.querySelectorAll('.add-new-multiple-btn').forEach(button => {
        button.addEventListener('click', function() {
            const fieldName = this.dataset.fieldName;
            const modelName = this.dataset.modelName;
            const createUrl = this.previousElementSibling.dataset.createUrl;

            let message = "";
            switch (modelName) {
                case "Artist":
                    message = "Entrez le nom complet du nouvel artiste : ";
                    break;
                case "ArtType":
                    message = "Entrez le nom du nouveau type d'Art : ";
                    break;
                case "Support":
                    message = "Entrez le nom du nouveau matériau à ajouter aux supports : ";
                    break;
                case "Technique":
                    message = "Entrez le nom de la technique à ajouter à la liste : ";
                    break;
                case "Collection":
                    message = "Entrez le nom de la Collection à créer : ";
                    break;
                case "Exhibition":
                    message = "Entrez le nom de la nouvelle expo à ajouter : ";
                    break;
                default:
                    message = `Entrez le nom de la nouvelle entrée pour: ${modelName} :`;
            }

            const name = prompt(message);
            if (name && name.trim()) {
                createNewMultipleOption(createUrl, name.trim(), fieldName);
            }
        });
    });
    // Auto-complétion pour les mots-clés
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
        
        // Masquer les suggestions quand on clique ailleurs
        document.addEventListener('click', function(e) {
            if (!input.parentElement.contains(e.target)) {
                suggestionsContainer.style.display = 'none';
            }
        });

        // Gestion de la touche Entrée pour créer un mot-clé
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
});

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
            // Ajouter la nouvelle option au select
            const select = document.querySelector(`[name="${fieldName}"]`);
            const option = new Option(data.name, data.id, true, true);
            select.add(option);
            
            if (data.created) {
                alert(`${data.name} a été ajouté avec succès !`);
            } else {
                alert(`${data.name} existait déjà et a été sélectionné.`);
            }
        } else {
            alert(`Erreur : ${data.error}`);
        }
    })
    .catch(error => {
        alert(`Erreur : ${error.message}`);
    });
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
            // Ajouter la nouvelle option au select multiple
            const select = document.querySelector(`[name="${fieldName}"]`);
            const option = new Option(data.name, data.id, false, false);
            select.add(option);
            
            // Sélectionner automatiquement la nouvelle option
            option.selected = true;
            
            // Déclencher l'événement change pour que les frameworks détectent le changement
            select.dispatchEvent(new Event('change'));
            
            if (data.created) {
                alert(`${data.name} a été ajouté avec succès et sélectionné !`);
            } else {
                alert(`${data.name} existait déjà et a été sélectionné.`);
            }
        } else {
            alert(`Erreur : ${data.error}`);
        }
    })
    .catch(error => {
        alert(`Erreur : ${error.message}`);
    });
}

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
            const afterCurrentTerm = '';
            const newValue = beforeLastComma + (beforeLastComma.endsWith(',') ? ' ' : '') + result.text + ', ';
            
            input.value = newValue;
            container.style.display = 'none';
            input.focus();
        });
        
        suggestionsList.appendChild(li);
    });
    
    container.style.display = 'block';
} 

/* Nouveau : crée un mot-clé via AJAX, puis l’injecte dans l’input */
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
            input.value = prefix + (prefix.endsWith(',') ? ' ' : '') + data.name + ', ';
        } else {
            alert(`Erreur : ${data.error}`);
        }
    })
    .catch(err => {
        alert(`Erreur : ${err.message}`);
    });
} 