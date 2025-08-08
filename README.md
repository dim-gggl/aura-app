# <div align="center"> 🎨 Aura 🇬🇧 <br> *Live With Your Collection*

Collecting isn’t about putting things in storage. It’s about remembering, sharing, passing things on, and dreaming.
Aura keeps each piece alive: its story, its details, its images, its journeys.
Everything stays clear, accessible, ready when you are.
No instruction manuals, no hurdles — just open and find.
Your collection becomes a place you live in, not a file you ignore.
And it finally has the interface it deserves.

---

## Quick Install

```bash
git clone https://github.com/dim-gggl/aura-app.git
cd aura-app
python -m venv .venv
source .venv/bin/activate  # Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

* Generate a `SECRET_KEY` in `.env`.
* Migrate and load base data:

```bash
python manage.py migrate
python manage.py populate_art_data
python manage.py createsuperuser
```

* Run:

```bash
python manage.py runserver
```

* Open: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## Tech

* **Backend**: Python + Django
* **Frontend**: HTML, CSS, JS + Bootstrap 5
* **Database**: PostgreSQL / SQLite
* **Storage**: Amazon S3 / local
* **Key Libs**: `django-crispy-forms`, `django-filter`, `django-imagekit`, `weasyprint`, `whitenoise`

---

**Aura** — because your collection deserves more than a spreadsheet.


---

# <div align="center"> 🎨 Aura 🇫🇷 <br> *Vivre avec sa collection*

On ne collectionne pas pour classer. On collectionne pour se souvenir, montrer, transmettre, rêver.
Aura garde chaque œuvre vivante : son histoire, ses détails, ses images, ses changements d’adresse.
Tout est là, clair, accessible, prêt quand vous en avez besoin.
Pas de mode d’emploi compliqué, pas de friction : vous ouvrez, vous retrouvez.
Votre collection devient un espace où naviguer, pas un dossier à dépoussiérer.
Et elle a enfin l’interface qu’elle mérite.

---

## Installation rapide

```bash
git clone https://github.com/dim-gggl/aura-app.git
cd aura-app
python -m venv .venv
source .venv/bin/activate  # Windows : venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

* Générez un `SECRET_KEY` dans `.env`.
* Migrations + données de base :

```bash
python manage.py migrate
python manage.py populate_art_data
python manage.py createsuperuser
```

* Lancez :

```bash
python manage.py runserver
```

* Ouvrez : [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## Tech

* **Backend** : Python + Django
* **Frontend** : HTML, CSS, JS + Bootstrap 5
* **Base** : PostgreSQL / SQLite
* **Stockage** : Amazon S3 / local
* **Libs clés** : `django-crispy-forms`, `django-filter`, `django-imagekit`, `weasyprint`, `whitenoise`

---

**Aura** — parce que votre collection mérite mieux qu’un tableur.
