![](./aura-api-title.png)

## Documentation

Cette API REST permet de gérer une collection d'art (œuvres, artistes), des contacts professionnels et des notes personnelles. Elle est construite avec Django REST Framework et sécurisée par JWT.

- **Base URL (dev)**: `http://localhost:8000`
- **Préfixe API**: `/api/`
- **Format**: JSON (UTF-8)
- **Auth requise**: Oui (JWT ou session Django)

### Authentification

Deux méthodes sont supportées:

- **JWT Bearer** (recommandé pour les intégrations)
  - Obtenir un jeton:
    - `POST /api/auth/token/`
    - Corps:
```json
{
  "username": "<votre_login>",
  "password": "<votre_mot_de_passe>"
}
```  
- Réponse:  

```json
{
  "access": "<jwt_access>",
  "refresh": "<jwt_refresh>"
}
```
- Rafraîchir le jeton d'accès:
    - `POST /api/auth/token/refresh/`
    - Corps:
```json
{
  "refresh": "<jwt_refresh>"
}
```
  - Utilisation: ajouter l'en-tête `Authorization: Bearer <jwt_access>`

- **Session Django** (utile en développement si connecté à l'interface web)
  - Les cookies de session authentifient automatiquement les requêtes.

### En-têtes recommandés

- `Accept: application/json`
- `Content-Type: application/json`
- `Authorization: Bearer <jwt_access>` (si JWT)

### Pagination

- Les endpoints `artworks` et `artists` sont paginés (PageNumberPagination).
- Paramètres:
  - `page`: numéro de page (par défaut 1)
  - `page_size`: éléments par page (par défaut 20, maximum 100)
- Forme de réponse paginée:
```json
{
  "count": 123,
  "next": "http://localhost:8000/api/<ressource>/?page=3",
  "previous": "http://localhost:8000/api/<ressource>/?page=1",
  "results": [ /* éléments */ ]
}
```
- Les endpoints `contacts` et `notes` ne sont pas paginés par défaut et renvoient un tableau JSON.

### Limitation de débit (Rate limiting)

- Anonyme: `50/min`
- Authentifié: `200/min`
- En cas de dépassement: statut `429 Too Many Requests`.

### Portée utilisateur (User scoping)

Toutes les ressources sont isolées par utilisateur. Vous ne pouvez accéder qu’aux objets appartenant à votre compte. Les tentatives d'accès à des objets d'un autre utilisateur renvoient `404 Not Found`.

---

## Endpoints

### Artistes

- **Liste**: `GET /api/artists/` (paginé)
- **Détail**: `GET /api/artists/{id}/`
- **Créer**: `POST /api/artists/`
- **Mettre à jour**: `PUT /api/artists/{id}/` ou `PATCH /api/artists/{id}/`
- **Supprimer**: `DELETE /api/artists/{id}/`

Champs (JSON):
- `id` (entier)
- `name` (string)
- `birth_year` (entier|null)
- `death_year` (entier|null)

Exemple — créer un artiste:
```bash
curl -X POST "http://localhost:8000/api/artists/" \
  -H "Authorization: Bearer <jwt_access>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Claude Monet",
    "birth_year": 1840,
    "death_year": 1926
  }'
```

Réponse (201):
```json
{
  "id": 1,
  "name": "Claude Monet",
  "birth_year": 1840,
  "death_year": 1926
}
```

### Œuvres (artworks)

- **Liste**: `GET /api/artworks/` (paginé)
- **Détail**: `GET /api/artworks/{id}/`
- **Créer**: `POST /api/artworks/`
- **Mettre à jour**: `PUT /api/artworks/{id}/` ou `PATCH /api/artworks/{id}/`
- **Supprimer**: `DELETE /api/artworks/{id}/`

Champs (JSON):
- `id` (UUID)
- `title` (string)
- `year_created` (entier|null)
- `country` (string|null)
- `status` (string|null) — correspond à la localisation courante de l'œuvre. Valeurs autorisées:
  - `domicile`, `stockage`, `pretee`, `restauration`, `encadrement`, `restitution`, `vente`, `vendue`, `perdue`, `volée`, `autre`
- `artists` (liste d'objets Artiste en lecture seule)
- `artist_ids` (liste d'identifiants d'artistes en écriture; alias de `artists`)

Notes:
- `artist_ids` est requis pour lier des artistes lors de la création/mise à jour.
- Les œuvres sont paginées; utiliser `page` et `page_size`.

Exemple — créer une œuvre:
```bash
curl -X POST "http://localhost:8000/api/artworks/" \
  -H "Authorization: Bearer <jwt_access>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Nymphéas",
    "year_created": 1916,
    "country": "France",
    "status": "domicile",
    "artist_ids": [1]
  }'
```

Réponse (201 — tronquée):
```json
{
  "id": "a4f14c2a-7f3b-4d02-9a7a-0f1c2f77b3e1",
  "title": "Nymphéas",
  "year_created": 1916,
  "country": "France",
  "status": "domicile",
  "artists": [
    { "id": 1, "name": "Claude Monet", "birth_year": 1840, "death_year": 1926 }
  ]
}
```

### Contacts

- **Liste**: `GET /api/contacts/` (tableau JSON)
- **Détail**: `GET /api/contacts/{id}/`
- **Créer**: `POST /api/contacts/`
- **Mettre à jour**: `PUT /api/contacts/{id}/` ou `PATCH /api/contacts/{id}/`
- **Supprimer**: `DELETE /api/contacts/{id}/`

Champs (JSON):
- `id` (entier)
- `name` (string)
- `contact_type` (string; valeurs: `galerie`, `musee`, `collectionneur`, `expert`, `restaurateur`, `transporteur`, `assureur`, `autre`)
- `email` (string)
- `phone` (string)
- `address` (string)
- `website` (string)
- `notes` (string)
- `created_at` (datetime ISO)
- `updated_at` (datetime ISO)

Exemple — créer un contact:
```bash
curl -X POST "http://localhost:8000/api/contacts/" \
  -H "Authorization: Bearer <jwt_access>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Galerie Lumière",
    "contact_type": "galerie",
    "email": "contact@lumiere.example",
    "phone": "+33 1 23 45 67 89",
    "address": "10 Rue de l'Art, 75000 Paris",
    "website": "https://lumiere.example",
    "notes": "Spécialisée impressionnisme"
  }'
```

### Notes

- **Liste**: `GET /api/notes/` (tableau JSON)
- **Détail**: `GET /api/notes/{id}/`
- **Créer**: `POST /api/notes/`
- **Mettre à jour**: `PUT /api/notes/{id}/` ou `PATCH /api/notes/{id}/`
- **Supprimer**: `DELETE /api/notes/{id}/`

Champs (JSON):
- `id` (entier)
- `title` (string)
- `content` (string)
- `is_favorite` (bool)
- `created_at` (datetime ISO, lecture seule)
- `updated_at` (datetime ISO, lecture seule)

Recherche:
- Paramètre de requête `search` pour filtrer par titre ou contenu (contient, insensible à la casse):
  - `GET /api/notes/?search=monet`

Exemple — créer une note:
```bash
curl -X POST "http://localhost:8000/api/notes/" \
  -H "Authorization: Bearer <jwt_access>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Préparation expo",
    "content": "Lister les œuvres candidates",
    "is_favorite": true
  }'
```

---

## Codes de statut et erreurs

- `200 OK`: Requête réussie
- `201 Created`: Ressource créée
- `204 No Content`: Ressource supprimée
- `400 Bad Request`: Données invalides (détails dans `errors`)
- `401 Unauthorized`: Authentification requise ou jeton invalide/expiré
- `403 Forbidden`: Accès refusé
- `404 Not Found`: Ressource inexistante ou n'appartient pas à l'utilisateur
- `429 Too Many Requests`: Limite de débit atteinte

Exemple d'erreur de validation (400):
```json
{
  "title": ["Ce champ est obligatoire."]
}
```

Exemple d'erreur d'authentification (401):
```json
{
  "detail": "Les informations d’authentification n’ont pas été fournies."
}
```

---

## Bonnes pratiques

- Toujours envoyer/recevoir du JSON (`Content-Type` et `Accept`).
- Utiliser des UUID pour identifier les œuvres côté client.
- Respecter la pagination pour `artworks` et `artists`.
- Gérer le rafraîchissement de jeton avant expiration (access ~10 min, refresh ~7 jours).

## Remarques techniques

- L'API applique automatiquement un filtrage par utilisateur authentifié.
- Des filtres/tri supplémentaires peuvent être ajoutés ultérieurement; se référer aux en-têtes de version si introduits.


