from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import CsrfProtect


db = SQLAlchemy()
bootstrap = Bootstrap()
csrf = CsrfProtect()