from marshmallow import fields, post_load
from launcher import ma
from launcher.servers.models import LaunchableServer


class DescrExtraSchema(ma.Schema):
    color = fields.String()
    text = fields.String()


class DescriptionSchema(ma.Schema):
    text = fields.String(required=True)
    extra = fields.List(fields.Nested(DescrExtraSchema()))


class PlayersSchema(ma.Schema):
    max = fields.Integer(required=True)
    online = fields.Integer(required=True)


class VersionSchema(ma.Schema):
    name = fields.String(required=True)
    protocol = fields.String(required=True)


class ServerStatusSchema(ma.Schema):
    description = fields.Nested(DescriptionSchema(), required=True)
    players = fields.Nested(PlayersSchema(), required=True)
    version = fields.Nested(VersionSchema(), required=True)
    favicon = fields.String(required=True)


class LaunchableServerSchema(ma.Schema):
    id = fields.String(dump_only=True)
    name = fields.String(required=True)
    hostname = fields.String(required=True)
    status = fields.Nested(ServerStatusSchema(), dump_only=True)

    @post_load
    def make_server(self, data, **kwargs):
        return LaunchableServer(**data)
