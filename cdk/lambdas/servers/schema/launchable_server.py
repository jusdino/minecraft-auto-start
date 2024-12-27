from datetime import datetime, UTC

from marshmallow import pre_load
from marshmallow.fields import Nested, Boolean

from config import config
from schema import DateTimeDecimal
from schema.basic_server import BasicServerSchema
from schema.instance_config import InstanceConfigSchema


class LaunchableServerSchema(BasicServerSchema):
    launch_time = DateTimeDecimal(required=True, allow_none=False)
    online = Boolean(required=False, allow_none=False, load_default=False)
    instance_configuration = Nested(
        InstanceConfigSchema(),
        allow_none=False,
        load_default=InstanceConfigSchema().load({}),
    )

    @pre_load
    def load_launch_time(self, data, **kwargs):
        """
        The only time this should come out of the DB as None is for a new server.
        We'll just set the 'launch_time' to just older than the launcher timeout
        so that it is sorted towards the top of the server list, but is still launchable.
        """
        if data.get('launch_time') is None:
            data['launch_time'] = (datetime.now(tz=UTC) - config.launcher_timeout).timestamp()
        return data
