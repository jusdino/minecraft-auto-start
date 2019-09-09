import os

from flask import Flask, jsonify
from flask_bcrypt import Bcrypt
from flask_debugtoolbar import DebugToolbarExtension
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


# instantiate the extensions
bcrypt = Bcrypt()
toolbar = DebugToolbarExtension()
db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()


def create_app(script_info=None):

    # instantiate the app
    app = Flask(__name__)

    # set config
    app_settings = os.getenv(
        "APP_SETTINGS", "config.ProductionConfig"
    )
    app.config.from_object(app_settings)

    # set up extensions
    bcrypt.init_app(app)
    toolbar.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)

    # register blueprints
    from launcher.auth.views import auth_blueprint
    from launcher.ui.views import ng_ui_blueprint
    from launcher.base.views import base_blueprint
    from launcher.servers.views import servers_blueprint

    app.register_blueprint(base_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(ng_ui_blueprint, url_prefix='/ui')
    app.register_blueprint(servers_blueprint, url_prefix='/servers')

    # flask login
    from launcher.auth.models import User

    # error handlers
    @app.errorhandler(401)
    def unauthorized_page(error):
        return jsonify({'message': 'not authenticated'}), 401

    @app.errorhandler(403)
    def forbidden_page(error):
        return jsonify({'message': 'forbidden'}), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return jsonify({'message': 'not found'}), 404

    @app.errorhandler(500)
    def server_error_page(error):
        return jsonify({'message': 'internal server error'}), 500

    # shell context for flask cli
    @app.shell_context_processor
    def ctx():
        return {"app": app, "db": db}

    return app
