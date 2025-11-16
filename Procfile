web: gunicorn aura_app.wsgi --log-file -
release: python manage.py migrate --noinput && python manage.py collectstatic --noinput