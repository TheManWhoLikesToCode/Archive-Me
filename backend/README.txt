redis-server
celery -A tasks worker --loglevel INFO
gunicorn -w 4 'app:app'
flask run