from marshmallow import fields, post_load
from launcher import ma
from launcher.auth import User


class UserSchema(ma.Schema):
    email = fields.String(required=True)
    admin = fields.Boolean(required=True, default=False)

    password = fields.String(load_only=True)

    @post_load
    def make_server(self, data, **kwargs):
        return User(**data)
