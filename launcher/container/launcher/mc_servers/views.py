from flask import Blueprint, send_from_directory
from flask_login import login_required

mc_servers_blueprint = Blueprint("mc_servers", __name__, static_folder='static')


@mc_servers_blueprint.route("/")
def index():
    return mc_servers_blueprint.send_static_file('index.html')


@mc_servers_blueprint.route("/<path:path>")
def home(path):
    return send_from_directory(mc_servers_blueprint.static_folder, path)
