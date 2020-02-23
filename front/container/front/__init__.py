import os

import boto3
from flask import Flask, jsonify
from flask_bcrypt import Bcrypt
from flask_debugtoolbar import DebugToolbarExtension
from flask_marshmallow import Marshmallow


# instantiate the extensions
bcrypt = Bcrypt()
toolbar = DebugToolbarExtension()
dynamodb = boto3.resource('dynamodb')
ma = Marshmallow()


def create_app(script_info=None):

    # instantiate the app
    app = Flask(__name__)

    # set config
    app_settings = os.environ.get("APP_SETTINGS", "front.config.ProductionConfig")
    app.config.from_object(app_settings)

    # set up extensions
    bcrypt.init_app(app)
    toolbar.init_app(app)
    ma.init_app(app)

    # register blueprints
    from front.auth.views import auth_blueprint
    from front.ui.views import ng_ui_blueprint
    from front.base.views import base_blueprint
    from front.servers.views import servers_blueprint

    app.register_blueprint(base_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(ng_ui_blueprint, url_prefix='/ui')
    app.register_blueprint(servers_blueprint, url_prefix='/servers')

    # flask login
    from front.auth.models import User

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
        return {"app": app, "dynamodb": dynamodb}

    return app
