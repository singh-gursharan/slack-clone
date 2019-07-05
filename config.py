import os
from dotenv import load_dotenv
load_dotenv('.flaskenv')


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LANGUAGES = ['en', 'es']
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-know'
    ELASTICSEARCH_URL = None
    #os.environ.get('ELASTICSEARCH_URL')
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'