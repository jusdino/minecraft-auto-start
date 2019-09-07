import os

from flask import Flask, render_template
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_debugtoolbar import DebugToolbarExtension
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


# instantiate the extensions
login_manager = LoginManager()
bcrypt = Bcrypt()
toolbar = DebugToolbarExtension()
bootstrap = Bootstrap()
db = SQLAlchemy()
migrate = Migrate()


def create_app(script_info=None):

    # instantiate the app
    app = Flask(
        __name__,
        template_folder="./templates",
        static_folder="./static",
    )

    # set config
    app_settings = os.getenv(
        "APP_SETTINGS", "config.ProductionConfig"
    )
    app.config.from_object(app_settings)

    # set up extensions
    login_manager.init_app(app)
    bcrypt.init_app(app)
    toolbar.init_app(app)
    bootstrap.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    # register blueprints
    from launcher.auth.views import auth_blueprint
    from launcher.ui.views import ng_ui_blueprint

    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(ng_ui_blueprint, url_prefix='/ui')

    # flask login
    from launcher.auth.models import User

    login_manager.login_view = "user.login"
    login_manager.login_message_category = "danger"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.filter(User.id == int(user_id)).first()

    # error handlers
    @app.errorhandler(401)
    def unauthorized_page(error):
        return render_template("errors/401.json"), 401

    @app.errorhandler(403)
    def forbidden_page(error):
        return render_template("errors/403.json"), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/404.json"), 404

    @app.errorhandler(500)
    def server_error_page(error):
        return render_template("errors/500.json"), 500

    # shell context for flask cli
    @app.shell_context_processor
    def ctx():
        return {"app": app, "db": db}

    return app
