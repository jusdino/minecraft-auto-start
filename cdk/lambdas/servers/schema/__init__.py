from datetime import UTC, datetime
from decimal import Decimal
from marshmallow import Schema, EXCLUDE
from marshmallow.fields import String, DateTime


class ForgivingSchema(Schema):
    """
    A Schema that will just ignore any unexpected fields
    """
    class Meta:
        unknown = EXCLUDE


class DescriptionField(String):
    """
    Around v1.20.4, servers started returning 'description' as a string
    rather than a dict:
    ```
    >>> nineteen.status().description
    {'text': 'a Minecraft server!'}
    >>> twenty.status().description
    'a Minecraft server!'
    ```

    We'll reformat the old responses to fit the new behavior
    """
    def _deserialize(self, value, attr, data, **kwargs):
        value = self._map_description(value)
        return super()._deserialize(value, attr, data, **kwargs)

    def _map_description(self, value):
        if isinstance(value, dict):
            return value.get('text', '')
        return value


class DateTimeDecimal(DateTime):
    """
    Custom DateTime field that serializes to timestamps as Decimals
    """
    def __init__(self, **kwargs):
        super().__init__(format='timestamp', **kwargs)

    def _deserialize(self, value, attr, data, **kwargs) -> datetime:
        date_time = super()._deserialize(value, attr, data, **kwargs)
        # Forcing the datetime object to be timezone-aware
        return date_time.replace(tzinfo=UTC)

    def _serialize(self, value, attr, obj, **kwargs) -> Decimal:
        # We'll truncate to the nearest second, then cast to a Decimal, DynamoDB's preferred numeric type
        return Decimal(int(super()._serialize(value, attr, obj, **kwargs)))
