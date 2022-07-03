import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    """App default settings."""

    # app settings
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    UPLOADED_PHOTOS_DEST = 'images'
    SECRET_KEY = 'LICASsbvusLDSUAVBAVBUiivevpueBEVBPVB'
    SESSION_COOKIE_SECURE = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    ELASTICSEARCH_URL = os.environ.get(
        'ELASTICSEARCH_URL', 'http://localhost:9200')
    LANGUAGES = os.environ.get('LANGUAGES')
    PRODUCTS_PER_PAGE = int(os.environ.get('PRODUCTS_PER_PAGE', '3'))

    # mail settings

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = os.environ.get('MAIL_PORT')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # celery config
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')
    CELERY_CONFIG = {}

    # s3 config
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_DOMAIN = os.environ.get('AWS_DOMAIN')


class DevelopmentConfig(Config):
    """Development config setting."""

    DEBUG = True


class TestingConfig(Config):
    """Testing config testing."""

    DEBUG = True
    TESTING = True

    SQLALCHEMY_DATABASE_URI = os.environ.get('test_flask_store')


class ProductionConfig(Config):
    """Production environment settings."""


class StagingConfig(Config):
    """Staging area config settings."""


class ReleaseConfig(Config):
    """Release config settings."""


app_config = dict(
    development=DevelopmentConfig,
    testing=TestingConfig,
    production=ProductionConfig,
    staging=StagingConfig,
    release=ReleaseConfig
)
