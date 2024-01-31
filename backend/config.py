# config.py
from dotenv import load_dotenv
from celery import Celery, Task
from flask import Flask
import os
import sys


# Flask configuration
load_dotenv()

env = os.environ.get('ENVIRONMENT')

if env == 'dev':
    PORT = 5003
    DEBUG = False
elif env == 'prod':
    PORT = 5001
    DEBUG = False
else:
    print("Environment not specified. Please provide a valid environment.")
    sys.exit(1)

# Celery initialization and configuration
def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)
            
    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app

# Flask application initialization
def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(
        CELERY=dict(
            broker_url="redis://localhost",
            result_backend="redis://localhost",
            task_ignore_result=True,
        ),
    )
    app.config.from_prefixed_env()
    celery_init_app(app)
    return app