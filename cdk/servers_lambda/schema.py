from marshmallow import fields, post_load, pre_load, post_dump, Schema, EXCLUDE


class DescrExtraSchema(Schema):
    color = fields.String()
    text = fields.String()


class DescriptionSchema(Schema):
    text = fields.String(required=True, dump_default='Offline')
    extra = fields.List(fields.Nested(DescrExtraSchema()))


class PlayersSchema(Schema):
    max = fields.Integer(required=True, dump_default=0)
    online = fields.Integer(required=True, dump_default=0)


class VersionSchema(Schema):
    name = fields.String(required=True, dump_default="N/A")
    protocol = fields.String(required=True, dump_default="N/A")


class ServerStatusSchema(Schema):
    description = fields.Nested(
        DescriptionSchema(),
        load_default=DescriptionSchema().dumps({}),
        dump_default=DescriptionSchema().dumps({})
    )
    players = fields.Nested(
        PlayersSchema(),
        load_default=PlayersSchema().dump({}),
        dump_default=PlayersSchema().dump({})
    )
    version = fields.Nested(
        VersionSchema(),
        load_default=VersionSchema().dump({}),
        dump_default=VersionSchema().dump({})
    )
    favicon = fields.String(
        load_default=None,
        dump_default=None,
        allow_none=True
    )


class BasicServerSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String(required=True)
    hostname = fields.String(required=False)


class LaunchableServerSchema(BasicServerSchema):
    status = fields.Nested(ServerStatusSchema())
    status_time = fields.String(required=False)
    launch_time = fields.String(required=False, allow_none=True)
    launching = fields.String(dump_only=True)
    version = fields.Integer(dump_default=0, load_default=0)

    @pre_load
    def deserialize_status(self, data, **kwargs):
        schema = ServerStatusSchema()
        status = data.get('status')
        if isinstance(status, str):
            data['status'] = schema.loads(status)
        return data

    @post_dump
    def serialize_status(self, data, **kwargs):
        schema = ServerStatusSchema()
        status = data.get('status')
        if isinstance(status, dict):
            data['status'] = schema.dumps(status)
        return data
