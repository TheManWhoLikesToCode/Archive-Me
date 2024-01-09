import os

API_URL = ''


class Config:
    DEBUG = False
    PORT = 5002


class DevelopmentConfig(Config):
    DEBUG = True
    URL = '0.0.0.0'
    API_URL = '0.0.0.0/5001'


class ProductionConfig(Config):
    URL = '0.0.0.0'
    API_URL = 'https://api.archive-me.net'


def get_config():
    env = os.getenv('FLASK_ENV', 'development')
    return ProductionConfig if env == 'production' else DevelopmentConfig


config = get_config()
API_URL = config.API_URL
