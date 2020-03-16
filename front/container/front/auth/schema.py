from marshmallow import fields, post_load
from front import ma
from front.auth import FullUser


class UserSchema(ma.Schema):
    email = fields.String(required=True)
    admin = fields.Boolean(required=True, default=False)

    password = fields.String(load_only=True)

    @post_load
    def make_server(self, data, **kwargs):
        return FullUser(**data)
