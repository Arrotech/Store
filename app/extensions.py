from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import CsrfProtect
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_mail import Mail
from flask_babel import Babel
from flask_babel import lazy_gettext as _l
from flask_moment import Moment

babel = Babel()
mail = Mail()
login = LoginManager()
db = SQLAlchemy()
bootstrap = Bootstrap()
csrf = CsrfProtect()
jwtmanager = JWTManager()
moment = Moment()
