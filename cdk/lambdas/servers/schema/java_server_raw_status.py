from marshmallow.fields import Nested, String

from schema import ForgivingSchema, DescriptionField
from schema.players import PlayersSchema
from schema.version import VersionSchema


class JavaServerRawStatusSchema(ForgivingSchema):
    """
    For deserializing raw status from a JavaServer lookup
    """
    description = DescriptionField(required=True)
    version = Nested(
        VersionSchema(),
        required=True
    )
    players = Nested(
        PlayersSchema(),
        required=True
    )
    favicon = String(required=False, allow_none=True)