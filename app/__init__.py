from flask import Flask, request, current_app, json
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_login import LoginManager
from flask_babel import Babel
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_migrate import Migrate
from celery import Celery
from logging.handlers import RotatingFileHandler
import logging
from elasticsearch import Elasticsearch
import os


db = SQLAlchemy()
migrate = Migrate()
bootstrap = Bootstrap()
login = LoginManager()
login.login_view = 'auth.login'
babel = Babel()
moment = Moment()
celery =Celery('app', backend='redis://localhost:6379', broker='redis://localhost:6379') 
celery.conf.update(
    CELERY_TASK_RESULT_EXPIRES=60,
    CELERY_IMPORTS="app.main.worker",
)


def create_app(config_class=Config):
    slack_app_instance = Flask(__name__)
    slack_app_instance.config.from_object(config_class)
    db.init_app(slack_app_instance)
    migrate.init_app(slack_app_instance, db)
    bootstrap.init_app(slack_app_instance)
    login.init_app(slack_app_instance)
    babel.init_app(slack_app_instance)
    moment.init_app(slack_app_instance)

    celery.conf.update(slack_app_instance.config)
    slack_app_instance.elasticsearch = Elasticsearch([slack_app_instance.config['ELASTICSEARCH_URL']]) \
        if slack_app_instance.config['ELASTICSEARCH_URL'] else None

    from app.auth import bp as auth_bp
    slack_app_instance.register_blueprint(auth_bp)
    from app.main import bp as main_bp
    slack_app_instance.register_blueprint(main_bp)

    if not slack_app_instance.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,
                                        backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.DEBUG)
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.DEBUG)
        log.addHandler(file_handler)
        log.info('new logger by werkzeug')

        slack_app_instance.logger.addHandler(file_handler)
        slack_app_instance.logger.setLevel(logging.DEBUG)
        slack_app_instance.logger.info('Microblog startup')

    return slack_app_instance


from app import models