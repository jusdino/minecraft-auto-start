from flask import Blueprint, request, jsonify

from launcher.auth import encode_auth_token


auth_blueprint = Blueprint("user", __name__)


@auth_blueprint.route("/login", methods=["POST"])
def login():
    # TODO: check creds against an actual user db
    data = request.json
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Invalid credentials'}), 401
    # TODO: serialize / deserialize user object
    user = {
        'email': data['email']
    }
    token, expiry = encode_auth_token(user['email'])
    return jsonify({
        'user': user,
        'token': token.decode('utf-8'),
        'expires': expiry
    })
