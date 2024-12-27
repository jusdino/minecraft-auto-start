from marshmallow.fields import String, Integer
from marshmallow.validate import OneOf, ContainsNoneOf

from schema import ForgivingSchema


class InstanceConfigSchema(ForgivingSchema):
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
            '17',
            '21',
            '22'
        ])
    )
    s3_schematic_prefix = String(
        allow_none=True,
        load_default='common',
        validate=ContainsNoneOf(['/', '.'])
    )