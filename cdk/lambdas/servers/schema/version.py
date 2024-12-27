from marshmallow import pre_load
from marshmallow.fields import String, Integer

from schema import ForgivingSchema


class VersionSchema(ForgivingSchema):
    name = String(required=False, load_default="N/A")
    protocol = Integer(required=False, load_default=-1)

    @pre_load
    def deserialize_protocol(self, data, **kwargs):
        """
        At some point, MCStatus started returning protocol as a number instead of a string. We'll coerce to the new
        data type to be consistent.
        """
        if 'protocol' in data.keys() and isinstance(data['protocol'], str):
            try:
                data['protocol'] = int(data['protocol'])
            except ValueError:
                data['protocol'] = -1
        return data
