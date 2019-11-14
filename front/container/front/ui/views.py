from flask import Blueprint, send_from_directory

ng_ui_blueprint = Blueprint("ui", __name__, static_folder='static')


@ng_ui_blueprint.route("/")
def index():
    return ng_ui_blueprint.send_static_file('index.html')


@ng_ui_blueprint.route("/<path:path>")
def home(path):
    return send_from_directory(ng_ui_blueprint.static_folder, path)
