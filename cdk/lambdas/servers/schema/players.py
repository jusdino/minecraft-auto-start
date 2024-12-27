from marshmallow.fields import Integer

from schema import ForgivingSchema


class PlayersSchema(ForgivingSchema):
    max = Integer(required=False, load_default=0)
    online = Integer(required=False, load_default=0)
