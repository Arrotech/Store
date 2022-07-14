from flask import Flask
from elasticsearch import Elasticsearch

from instance.config import app_config
from app.extensions import db, bootstrap, csrf, jwtmanager, login, mail, babel, moment


def create_app(config_name='production'):
    """Create and configure app."""

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')

    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']], headers={'Accept': 'application/vnd.elasticsearch+json', 'Content-Type': 'application/vnd.elasticsearch+json'}) \
        if app.config['ELASTICSEARCH_URL'] else None

    from app.api.v1.models import models

    db.init_app(app)
    bootstrap.init_app(app)
    csrf.init_app(app)
    jwtmanager.init_app(app)
    login.init_app(app)
    mail.init_app(app)
    babel.init_app(app)
    moment.init_app(app)

    from app.api.v1 import store_v1

    app.register_blueprint(store_v1, url_prefix='/api/v1/')

    return app
