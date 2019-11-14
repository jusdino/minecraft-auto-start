from flask import Blueprint, request, jsonify, g

from front.auth import encode_auth_token, auth_required
from front.auth.models import User
from front.auth.schema import UserSchema

auth_blueprint = Blueprint('user', __name__)


@auth_blueprint.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Invalid credentials'}), 401
    user = User.get_user_by_email(data['email'])
    if user is None or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
    token, expiry = encode_auth_token(user)
    user_serializer = UserSchema()
    return jsonify({
        'user': user_serializer.dump(user),
        'token': token.decode('utf-8'),
        'expires': expiry
    })


@auth_blueprint.route('/whoami', methods=['GET'])
@auth_required('user')
def who_am_i():
    return jsonify({
        'id': g.user.id,
        'email': g.user.email,
        'scopes': g.user.scopes
    })
