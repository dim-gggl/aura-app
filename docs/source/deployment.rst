Deployment Guide
=================

This guide covers deploying Aura Art to production environments.

Production Checklist
--------------------

Before deploying to production, ensure:

* [ ] Debug mode is disabled
* [ ] Secret key is set and secure
* [ ] Database is configured for production
* [ ] Static files are collected
* [ ] Media files are properly served
* [ ] HTTPS is enabled
* [ ] Security headers are configured
* [ ] Logging is configured
* [ ] Backup strategy is in place

Server Requirements
-------------------

Minimum Requirements
~~~~~~~~~~~~~~~~~~~~

* **CPU**: 2 cores
* **RAM**: 4GB
* **Storage**: 20GB SSD
* **OS**: Ubuntu 20.04 LTS or CentOS 8

Recommended Requirements
~~~~~~~~~~~~~~~~~~~~~~~~

* **CPU**: 4+ cores
* **RAM**: 8GB+
* **Storage**: 50GB+ SSD
* **OS**: Ubuntu 22.04 LTS

Software Dependencies
~~~~~~~~~~~~~~~~~~~~~

* Python 3.11+
* PostgreSQL 13+
* Nginx
* Redis (for caching)
* SSL certificate

Deployment Options
------------------

Docker Deployment
~~~~~~~~~~~~~~~~~

1. Create a Dockerfile:

   .. code-block:: dockerfile

      FROM python:3.11-slim

      WORKDIR /app
      COPY requirements.txt .
      RUN pip install -r requirements.txt

      COPY . .
      RUN python manage.py collectstatic --noinput

      EXPOSE 8000
      CMD ["gunicorn", "aura_app.wsgi:application"]

2. Create docker-compose.yml:

   .. code-block:: yaml

      version: '3.8'
      services:
        web:
          build: .
          ports:
            - "8000:8000"
          environment:
            - DEBUG=False
            - DATABASE_URL=postgresql://user:pass@db:5432/aura_art
          depends_on:
            - db
            - redis

        db:
          image: postgres:13
          environment:
            - POSTGRES_DB=aura_art
            - POSTGRES_USER=user
            - POSTGRES_PASSWORD=pass
          volumes:
            - postgres_data:/var/lib/postgresql/data

        redis:
          image: redis:6-alpine

        nginx:
          image: nginx:alpine
          ports:
            - "80:80"
            - "443:443"
          volumes:
            - ./nginx.conf:/etc/nginx/nginx.conf
            - ./static:/var/www/static
            - ./media:/var/www/media
          depends_on:
            - web

      volumes:
        postgres_data:

Traditional Deployment
~~~~~~~~~~~~~~~~~~~~~~

1. Set up the server:

   .. code-block:: bash

      # Update system
      sudo apt update && sudo apt upgrade -y

      # Install Python and dependencies
      sudo apt install python3.11 python3.11-venv python3-pip

      # Install PostgreSQL
      sudo apt install postgresql postgresql-contrib

      # Install Nginx
      sudo apt install nginx

      # Install Redis
      sudo apt install redis-server

2. Create application user:

   .. code-block:: bash

      sudo adduser aura-app
      sudo usermod -aG www-data aura-app

3. Deploy the application:

   .. code-block:: bash

      sudo -u aura-app git clone <repository-url> /home/aura-app/app
      cd /home/aura-app/app
      sudo -u aura-app python3.11 -m venv .venv
      sudo -u aura-app .venv/bin/pip install -r requirements.txt

4. Configure the database:

   .. code-block:: bash

      sudo -u postgres createdb aura_art
      sudo -u postgres createuser aura-app
      sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE aura_art TO aura-app;"

5. Run migrations:

   .. code-block:: bash

      sudo -u aura-app .venv/bin/python manage.py migrate
      sudo -u aura-app .venv/bin/python manage.py collectstatic

6. Create systemd service:

   .. code-block:: ini

      [Unit]
      Description=Aura Art Gunicorn daemon
      After=network.target

      [Service]
      User=aura-app
      Group=www-data
      WorkingDirectory=/home/aura-app/app
      ExecStart=/home/aura-app/app/.venv/bin/gunicorn --workers 3 --bind unix:/home/aura-app/app/aura_app.sock aura_app.wsgi:application
      Restart=always

      [Install]
      WantedBy=multi-user.target

7. Configure Nginx:

   .. code-block:: nginx

      server {
          listen 80;
          server_name your-domain.com;

          location /static/ {
              alias /home/aura-app/app/static/;
          }

          location /media/ {
              alias /home/aura-app/app/media/;
          }

          location / {
              include proxy_params;
              proxy_pass http://unix:/home/aura-app/app/aura_app.sock;
          }
      }

Environment Configuration
-------------------------

Production Settings
~~~~~~~~~~~~~~~~~~~

Configure production settings in ``production.py``:

.. code-block:: python

   DEBUG = False
   ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']
   
   # Database
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'aura_art',
           'USER': 'aura-app',
           'PASSWORD': 'secure_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   
   # Security
   SECURE_SSL_REDIRECT = True
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   SECURE_BROWSER_XSS_FILTER = True
   SECURE_CONTENT_TYPE_NOSNIFF = True

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

Set production environment variables:

.. code-block:: bash

   export DEBUG=False
   export SECRET_KEY="your-secret-key"
   export DATABASE_URL="postgresql://user:pass@localhost:5432/aura_art"
   export ALLOWED_HOSTS="your-domain.com,www.your-domain.com"

SSL Configuration
-----------------

Let's Encrypt Setup
~~~~~~~~~~~~~~~~~~~

1. Install Certbot:

   .. code-block:: bash

      sudo apt install certbot python3-certbot-nginx

2. Obtain SSL certificate:

   .. code-block:: bash

      sudo certbot --nginx -d your-domain.com -d www.your-domain.com

3. Configure auto-renewal:

   .. code-block:: bash

      sudo crontab -e
      # Add: 0 12 * * * /usr/bin/certbot renew --quiet

Monitoring and Logging
----------------------

Log Configuration
~~~~~~~~~~~~~~~~~

Configure logging for production:

.. code-block:: python

   LOGGING = {
       'version': 1,
       'disable_existing_loggers': False,
       'formatters': {
           'verbose': {
               'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
               'style': '{',
           },
       },
       'handlers': {
           'file': {
               'level': 'INFO',
               'class': 'logging.handlers.RotatingFileHandler',
               'filename': '/var/log/aura-app/django.log',
               'maxBytes': 1024*1024*15,  # 15MB
               'backupCount': 10,
               'formatter': 'verbose',
           },
       },
       'root': {
           'handlers': ['file'],
           'level': 'INFO',
       },
   }

Health Checks
~~~~~~~~~~~~~

Implement health check endpoints:

.. code-block:: python

   from django.http import JsonResponse
   from django.db import connection

   def health_check(request):
       try:
           connection.ensure_connection()
           return JsonResponse({'status': 'healthy'})
       except Exception as e:
           return JsonResponse({'status': 'unhealthy', 'error': str(e)}, status=500)

Backup Strategy
---------------

Database Backups
~~~~~~~~~~~~~~~~

Set up automated database backups:

.. code-block:: bash

   #!/bin/bash
   # backup_db.sh
   
   BACKUP_DIR="/var/backups/aura-app"
   DATE=$(date +%Y%m%d_%H%M%S)
   
   mkdir -p $BACKUP_DIR
   
   pg_dump -h localhost -U aura-app aura_art > $BACKUP_DIR/aura_art_$DATE.sql
   
   # Keep only last 30 days of backups
   find $BACKUP_DIR -name "*.sql" -mtime +30 -delete

Media Backups
~~~~~~~~~~~~~

Backup media files:

.. code-block:: bash

   #!/bin/bash
   # backup_media.sh
   
   BACKUP_DIR="/var/backups/aura-app/media"
   MEDIA_DIR="/home/aura-app/app/media"
   DATE=$(date +%Y%m%d_%H%M%S)
   
   mkdir -p $BACKUP_DIR
   
   tar -czf $BACKUP_DIR/media_$DATE.tar.gz -C $MEDIA_DIR .
   
   # Keep only last 30 days of backups
   find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

Performance Optimization
-------------------------

Caching Setup
~~~~~~~~~~~~~

Configure Redis caching:

.. code-block:: python

   CACHES = {
       'default': {
           'BACKEND': 'django.core.cache.backends.redis.RedisCache',
           'LOCATION': 'redis://127.0.0.1:6379/1',
           'OPTIONS': {
               'CLIENT_CLASS': 'django_redis.client.DefaultClient',
           }
       }
   }

Database Optimization
~~~~~~~~~~~~~~~~~~~~~~

Optimize database performance:

* Add database indexes for frequently queried fields
* Use database connection pooling
* Configure query optimization
* Set up read replicas for heavy read operations

Static File Optimization
~~~~~~~~~~~~~~~~~~~~~~~~

Optimize static file delivery:

* Use CDN for static files
* Enable gzip compression
* Set appropriate cache headers
* Minify CSS and JavaScript

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**502 Bad Gateway**
   Check if Gunicorn is running and the socket file exists.

**Static files not loading**
   Ensure static files are collected and Nginx is configured correctly.

**Database connection errors**
   Verify database credentials and connection settings.

**Permission errors**
   Check file permissions and user ownership.

**SSL certificate issues**
   Verify certificate installation and renewal status.

Monitoring Tools
~~~~~~~~~~~~~~~~

Recommended monitoring tools:

* **Application monitoring**: Sentry, Rollbar
* **Server monitoring**: Prometheus, Grafana
* **Log aggregation**: ELK Stack, Fluentd
* **Uptime monitoring**: Pingdom, UptimeRobot
