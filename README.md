# <div align="center"> 🇺🇸 Aura <br> *Art Collection Management*

Aura is a comprehensive web application designed for the discerning art collector. It offers a secure, user-friendly, and powerful interface to meticulously catalog, manage, and track every detail of an artwork's lifecycle, from initial acquisition and documentation to exhibition, loan, and potential sale. Aura transforms the administrative task of collection management into an elegant and insightful experience.

## Key Features

Aura is built with a rich set of features to provide a complete, end-to-end solution for managing a sophisticated art collection.

#### **Comprehensive Artwork Cataloging**

Go beyond simple lists and spreadsheets. Aura allows you to create a detailed, digital dossier for each artwork with an extensive set of fields, ensuring no critical detail is ever lost.

-   **Core Information**: Capture the essentials, including the artwork's title, its creator(s), the creation year, and its country of origin.
-   **Artistic Details**: Document the specific art type (e.g., Painting, Sculpture, Photography), the support medium (e.g., Canvas, Wood, Paper), and the techniques employed (e.g., Oil, Acrylic, Mixed Media).
-   **Physical Attributes**: Record precise physical dimensions (height, width, depth) and weight, which is crucial for shipping, storage, and installation planning.
-   **Acquisition & Provenance**: Track the complete acquisition history, including the date, place, and price. Maintain a detailed and chronological history of ownership (provenance), which is vital for authentication and valuation.
-   **Dynamic Status & Location**: Always know the exact status and whereabouts of your art. Use clear fields to define its current location (e.g., Home, Storage, On Loan, At a Gallery) and status flags (e.g., Framed, Signed, Under Restoration).
-   **Rich Photo Gallery**: Upload multiple high-resolution images for each piece. Capture the artwork from various angles, document signatures, or highlight specific details. You can set a primary photo for display and add descriptive captions to each image.

#### **Powerful Organization & Search**

Effortlessly manage and navigate your collection, no matter its size. Aura's tools are designed to provide quick and intuitive access to your data.

-   **Advanced Filtering & Search**: A powerful, multi-faceted filtering system allows you to query your collection by almost any metric. Find artworks by a specific artist, from a certain period, in a particular location, or tagged with specific keywords.
-   **Relational Entity Management**: The application features full CRUD (Create, Read, Update, Delete) functionality for all related entities, including **Artists**, **Collections**, and **Exhibitions**. The forms are designed to allow on-the-fly creation; for example, if an artist isn't in your database yet, you can add them directly from the artwork creation form without interrupting your workflow.
-   **Professional Data Export**: Generate and export beautifully formatted data sheets for any artwork in both **HTML** and **PDF** formats. These are perfect for providing documentation to insurance companies, galleries, or for personal archival purposes.

#### **Integrated Productivity Tools**

Aura includes several modules designed to streamline your entire collection management workflow.

-   **Contact Book**: Maintain an organized address book of all your professional contacts. This dedicated CRM is perfect for keeping track of galleries, museums, fellow collectors, experts, restorers, and transport agents.
-   **Notepad**: A built-in note-taking feature allows you to jot down research, thoughts, or reminders. You can favorite important notes to pin them to your dashboard for quick access.
-   **Strategic Wishlist**: Do more than just dream about your next acquisition. Track artworks you wish to acquire, complete with priority levels, estimated prices, and source URLs, turning your wishlist into a strategic planning tool.

#### **Personalization and User Experience**

-   **Secure, Private Accounts**: Robust user authentication and a per-user data structure ensure that your collection's information remains private and secure.
-   **Customizable Themes**: Make the application your own. Personalize your experience by choosing from a variety of distinct visual themes (e.g., Elegant, Futuristic, Minimalist, Retro, Nature) directly from your profile settings.

## Tech Stack

Aura is built on a modern, robust, and scalable technology stack, chosen for its reliability and development speed.

-   **Backend**: **Python** with the **Django Framework**, providing a secure and feature-rich foundation.
-   **Frontend**: **HTML**, **CSS**, and vanilla **JavaScript**, styled with **Bootstrap 5** for a responsive and clean user interface.
-   **Database**: **PostgreSQL** for production environments ensures data integrity and performance, with **SQLite3** used for lightweight local development.
-   **File Storage**: **Amazon S3** is used for scalable, cloud-based media file storage in production, with local file storage for development.
-   **Key Libraries**:
    -   `django-crispy-forms` & `crispy-bootstrap5`: To render clean, beautiful, and accessible forms.
    -   `django-filter`: To power the advanced search and filtering system.
    -   `django-imagekit`: For on-the-fly image processing and thumbnail generation to optimize performance.
    -   `weasyprint`: For high-quality, professional-grade PDF exporting.
    -   `whitenoise`: For efficiently serving static files directly from the web server in production.

## Quickstart & Installation

Follow these detailed steps to get a local instance of Aura up and running on your machine.

1.  **Clone the Repository and Prepare Your Environment:**
    First, clone the project from the repository. Then, create and activate a Python virtual environment to isolate the project's dependencies.
    ```bash
    git clone https://github.com/dim-gggl/aura-app.git
    cd aura-app
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use: venv\Scripts\activate
    ```

2.  **Install Required Dependencies:**
    Install all the necessary Python packages listed in the `requirements.txt` file.
    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

3.  **Configure Your Local Environment:**
    -   The project uses a `.env` file to manage environment variables. Create your own by copying the provided example file.
        ```bash
        cp .env.example .env
        ```
    -   Open the newly created `.env` file in a text editor. Generate a new, unique `SECRET_KEY` for your application. The default database settings will use SQLite, which requires no further configuration for local development.

4.  **Set Up the Database:**
    -   Apply the database migrations to create the necessary tables and relationships in your database.
        ```bash
        python manage.py migrate
        ```
    -   Run the custom management command to populate the database with initial choices for dropdown menus like art types, supports, and techniques. This makes the application easier to use from the start.
        ```bash
        python manage.py populate_art_data
        ```
    -   Create a superuser account to be able to log in and access the admin interface.
        ```bash
        python manage.py createsuperuser
        ```

5.  **Run the Development Server:**
    Start the Django development server.
    ```bash
    python manage.py runserver
    ```
    You can now access the application by navigating to `http://127.0.0.1:8000` in your web browser.

## Usage

Once the application is running, navigate to the site and **register** a new account or **log in** with the superuser credentials you created in the setup process. Upon logging in, you will be greeted by the main **dashboard**, which serves as your central hub for all collection-related activities.

From there, you can begin exploring the application's features. A good first step is to add a new **Artist** via the Artworks section, or you can dive right into adding an **Artwork**. The forms are designed to be intuitive, allowing you to create related items like artists or collections on the fly without ever leaving the page. To personalize your interface, visit your **Profile** from the user dropdown in the top-right corner and select a theme that suits your style.

---

# <div align="center"> 🇫🇷 Aura <br> *Gestion des collections d'art*

Aura est une application web complète conçue pour les collectionneurs d'art exigeants. Elle offre une interface sécurisée, conviviale et puissante pour cataloguer, gérer et suivre méticuleusement chaque détail du cycle de vie d'une œuvre d'art, depuis l'acquisition initiale et la documentation jusqu'à l'exposition, le prêt et la vente potentielle. Aura transforme la tâche administrative de la gestion des collections en une expérience élégante et perspicace.

## Caractéristiques principales

Aura est doté d'un riche ensemble de fonctionnalités qui en font une solution complète de bout en bout pour la gestion d'une collection d'œuvres d'art sophistiquée.

#### **Catalogue complet d'œuvres d'art**

Allez au-delà des simples listes et des feuilles de calcul. Aura vous permet de créer un dossier numérique détaillé pour chaque œuvre d'art avec un ensemble complet de champs, garantissant qu'aucun détail critique n'est jamais perdu.

- **Informations de base** : Saisissez l'essentiel, notamment le titre de l'œuvre, son ou ses créateurs, l'année de création et son pays d'origine.
- **Détails artistiques** : Documentez le type d'art spécifique (par exemple, peinture, sculpture, photographie), le support (par exemple, toile, bois, papier) et les techniques employées (par exemple, huile, acrylique, techniques mixtes).
- **Attributs physiques** : Enregistrez les dimensions physiques précises (hauteur, largeur, profondeur) et le poids, ce qui est crucial pour l'expédition, le stockage et la planification de l'installation.
- **Acquisition et provenance** : Suivez l'historique complet de l'acquisition, y compris la date, le lieu et le prix. Conservez un historique détaillé et chronologique de la propriété (provenance), ce qui est essentiel pour l'authentification et l'évaluation.
- **Statut dynamique et localisation** : Connaissez toujours l'état et l'emplacement exacts de vos œuvres d'art. Utilisez des champs clairs pour définir son emplacement actuel (par exemple, à la maison, dans un entrepôt, en prêt, dans une galerie) et les indicateurs d'état (par exemple, encadré, signé, en cours de restauration).
- **Galerie de photos riches** : Téléchargez plusieurs images haute résolution pour chaque œuvre. Capturez l'œuvre d'art sous différents angles, documentez les signatures ou mettez en évidence des détails spécifiques. Vous pouvez définir une photo principale à afficher et ajouter des légendes descriptives à chaque image.

#### **Organisation et recherche puissantes**

Gérez et parcourez votre collection sans effort, quelle que soit sa taille. Les outils d'Aura sont conçus pour fournir un accès rapide et intuitif à vos données.

- **Filtrage et recherche avancés** : Un système de filtrage puissant et polyvalent vous permet d'interroger votre collection en fonction de presque tous les critères. Trouvez des œuvres d'art d'un artiste spécifique, d'une certaine période, d'un lieu particulier, ou étiquetées avec des mots-clés spécifiques.
- **Gestion des entités relationnelles** : L'application offre une fonctionnalité CRUD (Create, Read, Update, Delete) complète pour toutes les entités liées, y compris **Artistes**, **Collections** et **Expositions**. Les formulaires sont conçus pour permettre la création à la volée ; par exemple, si un artiste n'est pas encore dans votre base de données, vous pouvez l'ajouter directement à partir du formulaire de création d'œuvre d'art sans interrompre votre flux de travail.
- **Exportation de données professionnelles** : Générez et exportez des fiches de données magnifiquement formatées pour n'importe quelle œuvre d'art aux formats **HTML** et **PDF**. Ces fiches sont parfaites pour fournir de la documentation aux compagnies d'assurance, aux galeries ou à des fins d'archivage personnel.

#### **Outils de productivité intégrés**

Aura comprend plusieurs modules conçus pour rationaliser l'ensemble de votre flux de travail de gestion des collections.

- **Carnet d'adresses** : Maintenez un carnet d'adresses organisé de tous vos contacts professionnels. Ce CRM dédié est parfait pour garder une trace des galeries, des musées, des collègues collectionneurs, des experts, des restaurateurs et des agents de transport.
- **Bloc-notes** : Une fonction de prise de notes intégrée vous permet de noter des recherches, des pensées ou des rappels. Vous pouvez mettre en favoris les notes importantes et les épingler sur votre tableau de bord pour y accéder rapidement.
- **Liste de souhaits stratégiques** : Ne vous contentez pas de rêver à votre prochaine acquisition. Suivez les œuvres d'art que vous souhaitez acquérir, avec les niveaux de priorité, les prix estimés et les URL des sources, transformant ainsi votre liste de souhaits en un outil de planification stratégique.

#### **Personnalisation et expérience utilisateur**

- **Comptes privés et sécurisés** : Une authentification robuste des utilisateurs et une structure de données par utilisateur garantissent que les informations de votre collection restent privées et sécurisées.
- **Thèmes personnalisables** : Faites de l'application la vôtre. Personnalisez votre expérience en choisissant parmi une variété de thèmes visuels distincts (par exemple, Élégant, Futuriste, Minimaliste, Rétro, Nature) directement à partir des paramètres de votre profil.

## Tech Stack

Aura est construit sur une pile technologique moderne, robuste et évolutive, choisie pour sa fiabilité et sa rapidité de développement.

- **Backend** : **Python** avec le **Django Framework**, fournissant une base sécurisée et riche en fonctionnalités.
- **Frontal** : **HTML**, **CSS**, et **JavaScript**, stylisé avec **Bootstrap 5** pour une interface utilisateur réactive et propre.
- **Base de données** : **PostgreSQL** pour les environnements de production assure l'intégrité des données et la performance, avec **SQLite3** utilisé pour le développement local léger.
- **Stockage de fichiers** : **Amazon S3** est utilisé pour le stockage de fichiers multimédias évolutifs dans le nuage en production, avec un stockage de fichiers local pour le développement.
- **Bibliothèques clés** :
    - `django-crispy-forms` & `crispy-bootstrap5` : Pour rendre des formulaires propres, beaux et accessibles.
    - `django-filter` : Pour alimenter le système de recherche avancée et de filtrage.
    - `django-imagekit` : Pour le traitement des images à la volée et la génération de vignettes afin d'optimiser les performances.
    - `weasyprint` : Pour l'exportation de PDF de haute qualité et de niveau professionnel.
    - `whitenoise` : Pour servir efficacement des fichiers statiques directement depuis le serveur web en production.

## Démarrage rapide et installation

Suivez ces étapes détaillées pour mettre en place une instance locale d'Aura sur votre machine.

1.  **Cloner le dépôt et préparer votre environnement:**
    Tout d'abord, clonez le projet à partir du référentiel. Ensuite, créez et activez un environnement virtuel Python pour isoler les dépendances du projet.
    ```bash
    git clone <votre-repository-url>
    cd aura-app
    python -m venv .venv
    source .venv/bin/activate # Sous Windows, utilisez : venv\Scripts\activate
    ```

2.  **Installer les dépendances requises:**
    Installez tous les paquets Python nécessaires listés dans le fichier `requirements.txt`.
    ``bash
    pip install -r requirements.txt
    ```

3.  **Configurer votre environnement local:**
    - Le projet utilise un fichier `.env` pour gérer les variables d'environnement. Créez le vôtre en copiant le fichier d'exemple fourni.
        ``bash
        cp .env.example .env
        ```
    - Ouvrez le fichier `.env` nouvellement créé dans un éditeur de texte. Générez un nouveau `SECRET_KEY` unique pour votre application. Les paramètres par défaut de la base de données utilisent SQLite, ce qui ne nécessite aucune configuration supplémentaire pour le développement local.

4.  **Configurer la base de données:**
    - Appliquez les migrations de base de données pour créer les tables et les relations nécessaires dans votre base de données.
        ``bash
        python manage.py migrate
        ```
    - Exécutez la commande de gestion personnalisée pour remplir la base de données avec des choix initiaux pour les menus déroulants tels que les types d'art, les supports et les techniques. Cela rend l'application plus facile à utiliser dès le départ.
        ``bash
        python manage.py populate_art_data
        ```
    - Créez un compte superutilisateur pour pouvoir vous connecter et accéder à l'interface d'administration.
        ``bash
        python manage.py createsuperuser
        ```

5.  **Exécuter le serveur de développement :**
    Démarrez le serveur de développement de Django.
    ```bash
    python manage.py runserver
    ```
    Vous pouvez maintenant accéder à l'application en naviguant vers `http://127.0.0.1:8000` dans votre navigateur web.

## Utilisation

Une fois l'application lancée, rendez-vous sur le site et **enregistrez** un nouveau compte ou **connectez-vous** avec les informations d'identification du super-utilisateur que vous avez créées au cours du processus d'installation. Une fois connecté, vous serez accueilli par le **tableau de bord** principal, qui vous servira de centre pour toutes les activités liées à la collecte.

A partir de là, vous pouvez commencer à explorer les fonctionnalités de l'application. Une bonne première étape consiste à ajouter un nouvel **artiste** via la section Œuvres d'art, ou vous pouvez directement ajouter une **œuvre d'art**. Les formulaires sont conçus pour être intuitifs, vous permettant de créer des éléments connexes tels que des artistes ou des collections à la volée sans jamais quitter la page. Pour personnaliser votre interface, visitez votre **Profil** dans le menu déroulant de l'utilisateur dans le coin supérieur droit et sélectionnez un thème qui correspond à votre style.



