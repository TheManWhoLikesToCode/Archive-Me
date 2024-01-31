redis-server
celery -A tasks worker --loglevel INFO
flask run