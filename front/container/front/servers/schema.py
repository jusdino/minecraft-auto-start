from marshmallow import fields, post_load
from front import ma
from front.servers.models import LaunchableServer


class DescrExtraSchema(ma.Schema):
    color = fields.String()
    text = fields.String()


class DescriptionSchema(ma.Schema):
    text = fields.String(required=True, default='Offline')
    extra = fields.List(fields.Nested(DescrExtraSchema()))


class PlayersSchema(ma.Schema):
    max = fields.Integer(required=True, default=0)
    online = fields.Integer(required=True, default=0)


class VersionSchema(ma.Schema):
    name = fields.String(required=True, default="N/A")
    protocol = fields.String(required=True, default="N/A")


class ServerStatusSchema(ma.Schema):
    description = fields.Nested(DescriptionSchema(), required=True, default=DescriptionSchema().dumps({}))
    players = fields.Nested(PlayersSchema(), required=True, default=PlayersSchema().dump({}))
    version = fields.Nested(VersionSchema(), required=True, default=VersionSchema().dump({}))
    favicon = fields.String(required=True, default='X')


class LaunchableServerSchema(ma.Schema):
    name = fields.String(required=True)
    hostname = fields.String(required=True)
    status = fields.Nested(ServerStatusSchema(), dump_only=True)

    @post_load
    def make_server(self, data, **kwargs):
        return LaunchableServer(**data)
