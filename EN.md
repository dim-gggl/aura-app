[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://docs.astral.sh/uv/)
[![Static Badge](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-%233775A9?style=plastic&logo=python&logoColor=%23FFE569)](https://www.python.org/)
[![Static Badge](https://img.shields.io/badge/django-5.2.5-%2344B78B?style=plastic&logo=django&logoColor=%2344B78B)](https://www.djangoproject.com/)
[![Static Badge](https://img.shields.io/badge/djangorestframework-3.16.1-%23FF474A?style=plastic&logo=django&logoColor=%23FF474A)](https://www.django-rest-framework.org/)  
[![GitHub License](https://img.shields.io/github/license/dim-gggl/aura-app?style=plastic&logo=MIT)](./LICENSE.md)
![GitHub last commit](https://img.shields.io/github/last-commit/dim-gggl/aura-app?display_timestamp=author&style=plastic)

![](./aura-title.png)

# <div align="center"> *Living with your collection*</div>

We don't collect to classify. We collect to remember, to show, to pass on, to dream. Aura keeps each work alive: its history, its details, its images, its journeys. Everything is clear, accessible and ready when you need it.

---

## 5-minute start-up

### 1) Clone and install dependencies

```bash
git clone https://github.com/dim-gggl/aura-app.git
cd aura-app
python3 -m venv .venv
source .venv/bin/activate # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
cp env.example .env
```

Edit `.env` then :

- **SECRET_KEY**: generate a key (e.g. via [ClinKey](https://dim-gggl.github.io/ClinKey/)).
- DEBUG**: leave `True` local.
- **DATABASE_URL**: optional (default is SQLite). Examples:
  - SQLite (default): nothing to do
  - PostgreSQL: `postgres://USER:PASS@localhost:5432/aura`

### 2) Initialize the database

Always run these initialization commands :

```bash
python manage.py migrate
python manage.py populate_art_data
python manage.py createsuperuser
```

### 3) Choose your dataset  


- Option A - **Empty database** (repositories only): do nothing further.
- Option B - **Full database (dummy works)**: import dummy data.

```bash
# attach works to created user (replace <your_user>)
python manage.py import_fake_artworks --username <your_user>

# optional: custom file (default: setup/fill_up/fake_artworks.json)
python manage.py import_fake_artworks --path setup/fill_up/fake_artworks.json --username <your_user>
```

Remarks:

- Art types, media and techniques are created by `populate_art_data`.
- Reference artists are loaded automatically from `setup/fill_up/artists.json` if present.

### 4) Launch the server

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000`, log in with the superuser you've created.

---

## User experience

### Empty base (Option A)
- Home screens and dashboard**: clear entry points, guided empty states.
- Create your first work**: simple forms, typed fields (art type, medium, technique, etc.).
- Contacts & notes**: add professionals and personal notes linked to your works.

### Full base (Option B)
- Browse** a realistic collection: list of works with search, filters and sorting.
- Rich details**: artists, collections, exhibitions, tags, provenance, location.
- Tools**: exports (e.g. PDF), suggestions, dedicated work/collection/exhibition views.
- Ideal game** for testing filters, detailed views and global navigation.

---

## Useful commands

```bash
# Reset (deletes data, keeps schema)
python manage.py flush --noinput

# Create a new admin
python manage.py createsuperuser

# Import fake artworks for another user
python manage.py import_fake_artworks --username demo
```

---

## Stack

- Backend**: Django
- Frontend** : HTML/CSS/JS (Bootstrap 5)
- Database**: SQLite (local) or PostgreSQL
- **Storage**: local or S3 (optional)
- Key libraries**: `django-crispy-forms`, `django-filter`, `django-imagekit`, `weasyprint`, `whitenoise`, `djangorestframework`

---

**Aura** - because your collection deserves more than a spreadsheet.
