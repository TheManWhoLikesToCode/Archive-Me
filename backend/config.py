import os

API_URL = ''
class Config:
    DEBUG = False
    PORT = 5001


class DevelopmentConfig(Config):
    DEBUG = True
    URL = 'http://localhost:5001'
    API_URL = 'http://localhost:5001/'


class ProductionConfig(Config):
    URL = '0.0.0.0'
    API_URL = 'https://api.archive-me.net/api'


def get_config():
    env = os.environ.get('FLASK_ENV', 'development')
    match env:
        case 'production':
            return ProductionConfig
        case _:
            return DevelopmentConfig


config = get_config()
API_URL = config.API_URL
