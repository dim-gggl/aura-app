[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://docs.astral.sh/uv/)
[![Static Badge](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-%233775A9?style=plastic&logo=python&logoColor=%23FFE569)](https://www.python.org/)
[![Static Badge](https://img.shields.io/badge/django-5.2.5-%2344B78B?style=plastic&logo=django&logoColor=%2344B78B)](https://www.djangoproject.com/)
[![Static Badge](https://img.shields.io/badge/djangorestframework-3.16.1-%23FF474A?style=plastic&logo=django&logoColor=%23FF474A)](https://www.django-rest-framework.org/)  
[![GitHub License](https://img.shields.io/github/license/dim-gggl/aura-app?style=plastic&logo=MIT)](./LICENSE.md)
![GitHub last commit](https://img.shields.io/github/last-commit/dim-gggl/aura-app?display_timestamp=author&style=plastic)

![](./aura-title.png)

# <div align="center"> *Vivre avec sa collection*</div>

On ne collectionne pas pour classer. On collectionne pour se souvenir, montrer, transmettre, rêver. Aura garde chaque œuvre vivante : son histoire, ses détails, ses images, ses voyages. Tout est clair, accessible, prêt quand vous en avez besoin.

---

## Démarrage en 5 minutes

### 1) Cloner et installer les dépendances

```bash
git clone https://github.com/dim-gggl/aura-app.git
cd aura-app
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
cp env.example .env
```

Éditez `.env` puis :

- **SECRET_KEY**: générez une clé (ex. via [Djecrety](https://djecrety.ir/)).
- **DEBUG**: laissez `True` en local.
- **DATABASE_URL**: optionnel (par défaut SQLite). Exemples:
  - SQLite (défaut) : rien à faire
  - PostgreSQL : `postgres://USER:PASS@localhost:5432/aura`

### 2) Initialiser la base de données

Toujours exécuter ces commandes d’initialisation :

```bash
python manage.py migrate
python manage.py populate_art_data
python manage.py createsuperuser
```

### 3) Choisir votre jeu de données

- Option A — **Base vide** (référentiels seulement) : ne rien faire de plus.
- Option B — **Base pleine (fausses œuvres)** : importer les données factices.

```bash
# rattache les œuvres à l’utilisateur créé (remplacez <votre_user>)
python manage.py import_fake_artworks --username <votre_user>

# optionnel : fichier personnalisé (défaut: setup/fill_up/fake_artworks.json)
python manage.py import_fake_artworks --path setup/fill_up/fake_artworks.json --username <votre_user>
```

Remarques :

- Les types d’art, supports et techniques sont créés par `populate_art_data`.
- Les artistes de référence sont chargés automatiquement depuis `setup/fill_up/artists.json` s’il est présent.

### 4) Lancer le serveur

```bash
python manage.py runserver
```

Ouvrez `http://127.0.0.1:8000`, connectez‑vous avec le super‑utilisateur créé.

---

## Expérience utilisateur

### Base vide (Option A)
- **Écrans d’accueil et tableau de bord**: points d’entrée clairs, états vides guidés.
- **Créer votre première œuvre**: formulaires simples, champs typés (type d’art, support, technique, etc.).
- **Contacts & notes**: ajoutez des professionnels et des notes personnelles, liés à vos œuvres.

### Base pleine (Option B)
- **Parcourir** une collection réaliste : liste d’œuvres avec recherche, filtres et tris.
- **Détails riches**: artistes, collections, expositions, tags, provenance, localisation.
- **Outils**: exports (ex. PDF), suggestions, vues dédiées œuvre/collection/exposition.
- **Jeu idéal** pour tester filtres, vues détaillées, et la navigation globale.

---

## Commandes utiles

```bash
# Reset (efface les données, conserve le schéma)
python manage.py flush --noinput

# Créer un nouvel admin
python manage.py createsuperuser

# Import de fausses œuvres pour un autre utilisateur
python manage.py import_fake_artworks --username demo
```

---

## Stack

- **Backend** : Django
- **Frontend** : HTML/CSS/JS (Bootstrap 5)
- **Base de données** : SQLite (local) ou PostgreSQL
- **Stockage** : local ou S3 (optionnel)
- **Librairies clés** : `django-crispy-forms`, `django-filter`, `django-imagekit`, `weasyprint`, `whitenoise`, `djangorestframework`

---

**Aura** — parce que votre collection mérite mieux qu’un tableur.
