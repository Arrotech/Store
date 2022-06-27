from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import CsrfProtect
from flask_jwt_extended import JWTManager
from flask_login import LoginManager

login_manager = LoginManager()
db = SQLAlchemy()
bootstrap = Bootstrap()
csrf = CsrfProtect()
jwtmanager = JWTManager()
