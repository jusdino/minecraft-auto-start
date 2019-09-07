from flask import Blueprint, url_for
from flask.json import jsonify
from werkzeug.utils import redirect

from launcher.auth import auth_required

base_blueprint = Blueprint("base", __name__)


@base_blueprint.route('/healthcheck')
@auth_required
def healthcheck():
    return jsonify({'message': 'OK'})


@base_blueprint.route('/')
def index():
    return redirect(url_for('ui.index'), code=301)
