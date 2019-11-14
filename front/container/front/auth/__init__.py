from datetime import datetime, timezone
from functools import wraps

import jwt
from flask import request, current_app, g
from werkzeug.exceptions import abort

from front.auth.models import User


def auth_required(scope: str):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token_string = request.headers.get('authentication')
            if token_string is None:
                abort(401)

            try:
                token = decode_auth_token(token_string)
                if scope not in token['scopes']:
                    abort(403)
                g.token = token
                g.user = User.query.get(token['sub'])
            except jwt.InvalidTokenError:
                abort(401)

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def encode_auth_token(user):
    """
    Generates the Auth Token
    :return: string
    """
    now = datetime.now(tz=timezone.utc)
    expiry = now + current_app.config['TOKEN_TTL']
    expiry_timestamp = (expiry
                        - datetime(1970, 1, 1, tzinfo=timezone.utc)
                        ).total_seconds() * 1000
    payload = {
        'exp': expiry,
        'iat': now,
        'sub': user.id,
        'scopes': user.scopes
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256'), expiry_timestamp


def decode_auth_token(token_string):
    auth_type, value = token_string.split(maxsplit=1)
    if auth_type.lower() == 'bearer':
        return jwt.decode(token_string.split()[1], current_app.config['SECRET_KEY'], algorithms=['HS256'], verify=True)
    raise jwt.InvalidTokenError('Not a Bearer Token')
