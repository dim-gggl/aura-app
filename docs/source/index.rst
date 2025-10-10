Aura Art Documentation
=======================

Welcome to the Aura Art documentation! This Django application is designed to manage artworks, artists, collections, and exhibitions with a focus on art enthusiasts and collectors.

About Aura Art
--------------

Aura Art is a comprehensive Django web application that provides:

* **Artwork Management**: Catalog and organize your art collection
* **Artist Profiles**: Maintain detailed artist information and biographies
* **Collection Organization**: Group artworks into meaningful collections
* **Exhibition Tracking**: Plan and track art exhibitions
* **Contact Management**: Keep track of galleries, collectors, and art professionals
* **Notes System**: Add personal notes and observations about artworks
* **Export Functionality**: Export your data in various formats

Quick Start
-----------

To get started with Aura Art:

1. Install the required dependencies
2. Set up your database
3. Run migrations
4. Create a superuser account
5. Start the development server

For detailed installation instructions, see :doc:`installation`.

Architecture Overview
---------------------

The application is organized into several Django apps:

* **accounts**: User authentication and profile management
* **artworks**: Core artwork, artist, collection, and exhibition models
* **contacts**: Contact management for galleries and collectors
* **notes**: Note-taking system for artworks and artists
* **core**: Core functionality and utilities
* **services**: External services integration (images, PDF generation)

Live Application
----------------

Aura Art is deployed and accessible at: https://aura-art.org

The production deployment includes:
* Secure HTTPS access
* Global CDN for fast loading
* 24/7 monitoring and backups
* Regular updates and maintenance

API Documentation
-----------------

Aura Art provides a REST API for programmatic access to your data. See :doc:`api` for detailed API documentation.

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: Documentation:

   installation
   configuration
   models
   api
   deployment
   contributing

