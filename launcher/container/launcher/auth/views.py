from datetime import datetime, timezone

import jwt
from flask import Blueprint, request, current_app, jsonify


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


def encode_auth_token(user_id):
    """
    Generates the Auth Token
    :return: string
    """
    now = datetime.now(tz=timezone.utc)
    expiry_timestamp = (now + current_app.config['TOKEN_TTL']
                        - datetime(1970, 1, 1, tzinfo=timezone.utc)
                        ).total_seconds() * 1000
    payload = {
        'exp': expiry_timestamp,
        'iat': now,
        'sub': user_id
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256'), expiry_timestamp
