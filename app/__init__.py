from flask import Flask, current_app, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_babel import Babel, lazy_gettext as _l
from config import Config

import logging
from logging.handlers import SMTPHandler

mail = Mail()
db = SQLAlchemy()
migrate = Migrate()
babel = Babel()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = _l('Please log in to access this page.')


# factory design pattern :)
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    init_modules(app)

    register_blueprints(app)

    if not app.debug:
        setup_mail_debug(app)

    return app


def register_blueprints(application):
    from app.api import bp as api_bp
    application.register_blueprint(api_bp)

    from app.auth import bp as auth_bp
    application.register_blueprint(auth_bp)

    from app.errors import bp as errors_bp
    application.register_blueprint(errors_bp)

    from app.main import bp as main_bp
    application.register_blueprint(main_bp)

    from app.routes_drive import bp as routes_bp
    application.register_blueprint(routes_bp)

    from app.users import bp as users_bp
    application.register_blueprint(users_bp)

@babel.localeselector
def get_locale():
    return "nl"
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])

def init_modules(app):
    babel.init_app(app)
    mail.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)


def setup_mail_debug(app):
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='PlaceHolder Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


from app import models
from app.main import routes
