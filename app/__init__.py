from flask import Flask

from instance.config import app_config
from app.extensions import db, bootstrap


def create_app(config_name='production'):
    """Create and configure app."""

    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')

    from app.api.v1.models import models

    db.init_app(app)
    bootstrap.init_app(app)

    from app.api.v1 import store_v1

    app.register_blueprint(store_v1, url_prefix='/api/v1/')

    return app
