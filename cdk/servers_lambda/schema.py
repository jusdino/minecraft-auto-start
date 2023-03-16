from marshmallow import pre_load, post_dump, Schema, EXCLUDE
from marshmallow.fields import String, List, Integer, Nested
from marshmallow.validate import OneOf


class DescrExtraSchema(Schema):
    color = String()
    text = String()


class DescriptionSchema(Schema):
    text = String(required=True, dump_default='Offline')
    extra = List(Nested(DescrExtraSchema()))


class PlayersSchema(Schema):
    max = Integer(required=True, dump_default=0)
    online = Integer(required=True, dump_default=0)


class VersionSchema(Schema):
    name = String(required=True, dump_default="N/A")
    protocol = String(required=True, dump_default="N/A")


class ServerStatusSchema(Schema):
    description = Nested(
        DescriptionSchema(),
        load_default=DescriptionSchema().dumps({}),
        dump_default=DescriptionSchema().dumps({})
    )
    players = Nested(
        PlayersSchema(),
        load_default=PlayersSchema().dump({}),
        dump_default=PlayersSchema().dump({})
    )
    version = Nested(
        VersionSchema(),
        load_default=VersionSchema().dump({}),
        dump_default=VersionSchema().dump({})
    )
    favicon = String(
        load_default=None,
        dump_default=None,
        allow_none=True
    )


class BasicServerSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = String(required=True)
    hostname = String(required=False)


class InstanceConfigSchema(Schema):
    instance_type = String(
        allow_none=False,
        validate=OneOf(choices=[
            't3.medium',
            't3.large',
            't3.xlarge',
            't3.2xlarge'
        ]),
        load_default='t3.large'
    )
    volume_size = Integer(
        strict=False,
        allow_none=False,
        load_default=20
    )
    memory_size = String(
        allow_none=False,
        load_default='6144m'
    )
    java_version = String(
        allow_none=False,
        load_default='17',
        validate=OneOf(choices=[
            '8',
            '17'
        ])
    )


class LaunchableServerSchema(BasicServerSchema):
    status = Nested(ServerStatusSchema())
    status_time = String(required=False)
    launch_time = String(required=False, allow_none=True)
    launching = String(dump_only=True)
    version = Integer(dump_default=0, load_default=0)
    instance_configuration = Nested(
        InstanceConfigSchema(),
        allow_none=False,
        load_default=InstanceConfigSchema().load({}),
    )

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
