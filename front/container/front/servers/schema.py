from marshmallow import fields, post_load, pre_load, post_dump
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
    description = fields.Nested(DescriptionSchema(), missing=DescriptionSchema().dumps({}), default=DescriptionSchema().dumps({}))
    players = fields.Nested(PlayersSchema(), missing=PlayersSchema().dump({}), default=PlayersSchema().dump({}))
    version = fields.Nested(VersionSchema(), missing=VersionSchema().dump({}), default=VersionSchema().dump({}))
    favicon = fields.String(missing=None, default=None, allow_none=True)


class LaunchableServerSchema(ma.Schema):
    name = fields.String(required=True)
    hostname = fields.String(required=False)
    status = fields.Nested(ServerStatusSchema())
    status_time = fields.String(required=False)
    launch_time = fields.String(required=False, allow_none=True)
    launching = fields.String(dump_only=True)
    version = fields.Integer(default=0, missing=0)

    @pre_load
    def deserialize_status(self, data, **kwargs):
        schema = ServerStatusSchema()
        status = data.get('status')
        if isinstance(status, str):
            data['status'] = schema.loads(status)
        return data

    @post_load
    def make_server(self, data, **kwargs):
        return LaunchableServer(**data)

    @post_dump
    def serialize_status(self, data, **kwargs):
        schema = ServerStatusSchema()
        status = data.get('status')
        if isinstance(status, dict):
            data['status'] = schema.dumps(status)
        return data
