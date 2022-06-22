import os

class Config(object):
    """App default settings."""

    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')
    UPLOADED_PHOTOS_DEST = 'images'
    SECRET_KEY = 'LICASsbvusLDSUAVBAVBUiivevpueBEVBPVB'
    SESSION_COOKIE_SECURE = False


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
