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
    env = os.getenv('FLASK_ENV', 'development')
    return ProductionConfig if env == 'production' else DevelopmentConfig


config = get_config()
API_URL = config.API_URL
