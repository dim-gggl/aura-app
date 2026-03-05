Installation Guide
===================

This guide will help you install and set up Aura Art on your system.

Prerequisites
-------------

Docker Installation
~~~~~~~~~~~~~~~~~~~

For Docker installation, you only need:

* Docker and Docker Compose
* Git

Manual Installation
~~~~~~~~~~~~~~~~~~~

For manual installation, you need:

* Python 3.11 or higher
* pip or uv package manager
* PostgreSQL (recommended) or SQLite
* Git

Installation Steps
------------------

Docker Installation (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The easiest way to run Aura Art is using Docker Compose:

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/dim-gggl/aura-app.git
      cd aura-app

2. Set up environment variables:

   .. code-block:: bash

      cp env.example .env

   Edit the `.env` file with your configuration settings.

3. Start the application:

   .. code-block:: bash

      docker-compose up -d

4. Create a superuser account:

   .. code-block:: bash

      docker-compose exec web python manage.py createsuperuser

5. Load initial data (optional):

   .. code-block:: bash

      docker-compose exec web python manage.py loaddata setup/fill_up/artists.json
      docker-compose exec web python manage.py loaddata setup/fill_up/fake_artworks.json

You should now be able to access Aura Art at http://localhost:8000.

Manual Installation
~~~~~~~~~~~~~~~~~~~~~

If you prefer to install manually without Docker:

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/dim-gggl/aura-app.git
      cd aura-app

2. Create and activate a virtual environment:

   .. code-block:: bash

      python -m venv .venv
      source .venv/bin/activate  # On Windows: .venv\Scripts\activate

3. Install dependencies:

   .. code-block:: bash

      uv sync

   Or with pip:

   .. code-block:: bash

      pip install -r requirements.txt

4. Set up environment variables:

   .. code-block:: bash

      cp env.example .env

   Edit the `.env` file with your configuration settings.

5. Run database migrations:

   .. code-block:: bash

      python manage.py migrate

6. Create a superuser account:

   .. code-block:: bash

      python manage.py createsuperuser

7. Load initial data (optional):

   .. code-block:: bash

      python manage.py loaddata setup/fill_up/artists.json
      python manage.py loaddata setup/fill_up/fake_artworks.json

8. Start the development server:

   .. code-block:: bash

      python manage.py runserver

You should now be able to access Aura Art at http://localhost:8000.

Production Deployment
---------------------

Aura Art is deployed at https://aura-art.org. The production deployment includes:

* **HTTPS**: Secure SSL/TLS encryption
* **CDN**: Fast global content delivery
* **Monitoring**: 24/7 uptime monitoring
* **Backups**: Automated daily backups
* **Updates**: Regular security and feature updates

Access the live application at: https://aura-art.org

Configuration
-------------

Environment Variables
~~~~~~~~~~~~~~~~~~~~~~

The following environment variables can be configured in your `.env` file:

Tip: In order to generate a secure secret key, you can use Clinkey-Cli using pip:

.. code-block:: bash

   uv pip install clinkey-cli
   # or pip install clinkey-cli
   export DJANGO_SECRET_KEY=$(clinkey -l 64 -s - -t super_strong --lower)

* ``DEBUG``: Set to True for development, False for production
* ``SECRET_KEY``: Django secret key for security
* ``DATABASE_URL``: Database connection string
* ``ALLOWED_HOSTS``: Comma-separated list of allowed hosts
* ``EMAIL_HOST``: SMTP server for email functionality
* ``EMAIL_PORT``: SMTP port
* ``EMAIL_HOST_USER``: SMTP username
* ``EMAIL_HOST_PASSWORD``: SMTP password

Database Configuration
~~~~~~~~~~~~~~~~~~~~~~

Aura Art supports multiple database backends:

* **PostgreSQL** (recommended for production)
* **SQLite** (default for development)
* **MySQL**

For production deployments, PostgreSQL is strongly recommended for better performance and data integrity.

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**ImportError: No module named 'django'**
   Make sure your virtual environment is activated and Django is installed.

**Database connection errors**
   Verify your database settings in the `.env` file and ensure the database server is running.
   Depending on your PostgreSQL version, try running the following command (in a separate terminal):
   
   .. code-block:: bash
   
      pg_isready
   
   If this command fails, you may need to start PostgreSQL. On macOS with Homebrew, you can use:
   
   .. code-block:: bash
   
      brew services start postgresql
      # it's possible that you need to specify the version, like:
      # brew services start postgresql@16
   
   For Linux, you can use:
   
   .. code-block:: bash
   
      sudo systemctl start postgresql
   
   For Windows, you can use:
   
   .. code-block:: bash
   
      net start postgresql

**Permission errors**
   Make sure the application has proper permissions to write to the media and static directories.

Getting Help
------------

If you encounter issues during installation:

1. Check the troubleshooting section above
2. Review the Django documentation
3. Check the project's issue tracker
4. Contact the development team on GitHub : https://github.com/dim-gggl/aura-app/issues
