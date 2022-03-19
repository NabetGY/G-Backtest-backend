release: python manage.py migrate
web gunicorn core.wsgi --log-file -
worker: celery -A core worker --beat --scheduler django --loglevel=info
