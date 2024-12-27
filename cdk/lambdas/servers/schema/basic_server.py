import json
from datetime import datetime, UTC

from marshmallow import pre_load
from marshmallow.fields import Integer, String, Nested

from config import config
from schema import ForgivingSchema, DescriptionField, DateTimeDecimal
from schema.players import PlayersSchema
from schema.version import VersionSchema


class BasicServerSchema(ForgivingSchema):
    name = String(required=True)
    hostname = String(required=True)
    description = DescriptionField(
        required=False,
        allow_none=False,
        load_default='A Minecraft server'
    )
    mc_version = Nested(
        VersionSchema(),
        load_default=VersionSchema().load({})
    )
    favicon = String(
        load_default=None,
        allow_none=True
    )
    version = Integer(load_default=0, required=False)
    status_time = DateTimeDecimal(required=True, allow_none=False)
    players = Nested(
        PlayersSchema(),
        load_default=PlayersSchema().load({})
    )

    @pre_load
    def do_preloads(self, data, **kwargs):
        """
        Order matters for these steps, so we'll orchestrate from a single hook
        """
        data = self._deserialize_status(data, **kwargs)
        data = self._move_legacy_fields(data, **kwargs)
        data = self._load_status_time(data, **kwargs)
        return data

    def _load_status_time(self, data, **kwargs):
        """
        The only time this should come out of the DB as None is for a new server.
        We'll just set the 'status_time' to just older than the status timeout.
        """
        if data.get('status_time') is None:
            data['status_time'] = (datetime.now(tz=UTC) - config.server_status_ttl).timestamp()
        return data

    def _deserialize_status(self, data, **kwargs):
        status = data.get('status')
        if isinstance(status, str):
            data['status'] = json.loads(status)
        return data

    def _move_legacy_fields(self, data, **kwargs):
        """
        Legacy server records included all the JavaServer data under the
        'status' field. We'll move those to the new location.
        """
        try:
            data['description'] = data['status'].pop('description')
        except KeyError:
            pass
        try:
            data['mc_version'] = data['status']['version']
        except KeyError:
            pass
        try:
            data['favicon'] = data['status']['favicon']
        except KeyError:
            pass
        return data