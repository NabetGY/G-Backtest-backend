release: python manage.py migrate
web gunicorn core.wsgi --log-file -
worker: celery -A coreworker --beat --scheduler django --loglevel=info
