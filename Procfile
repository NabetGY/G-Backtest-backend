release: python manage.py migrate
web gunicorn core.wsgi --log-file -
worker: celery -A core worker --loglevel=info
beat: celery -A core beat -l info -S django
