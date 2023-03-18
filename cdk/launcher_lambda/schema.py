from marshmallow import Schema
from marshmallow.fields import String, Integer, Nested
from marshmallow.validate import OneOf, ContainsNoneOf


class InstanceConfigSchema(Schema):
    instance_type = String(
        allow_none=False,
        required=True,
        validate=OneOf(choices=[
            't3.medium',
            't3.large',
            't3.xlarge',
            't3.2xlarge'
        ])
    )
    volume_size = Integer(
        strict=True,
        allow_none=False,
        required=True
    )
    memory_size = String(
        allow_none=False,
        required=True
    )
    java_version = String(
        allow_none=False,
        required=True,
        validate=OneOf(choices=[
            '8',
            '17'
        ])
    )
    s3_schematic_prefix = String(
        allow_none=True,
        load_default='common',
        validate=ContainsNoneOf(['/', '.'])
    )


class InvokeEventSchema(Schema):
    """
    Schema for lambda invocation event payload

    Provides default values for instance configuration
    """
    server_name = String(required=True, allow_none=False)
    instance_configuration = Nested(
        InstanceConfigSchema(),
        allow_none=False,
        required=True
    )
