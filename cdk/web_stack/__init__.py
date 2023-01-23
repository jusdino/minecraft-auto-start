from constructs import Construct
from aws_cdk import Stack

from server_stack import ServerStack
from .api import Api
from .servers_api import ServersApi
from .ui import ServersUi
from .users import Users
from .launcher import Launcher


class WebStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, server_stack: ServerStack, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        rest_api = Api(self, 'Api').rest_api
        ServersUi(self, 'UI', rest_api=rest_api.root)
        users = Users(
            self, 'Users',
            domain_name=rest_api.domain_name.domain_name
        )
        launcher = Launcher(
            self, 'Launcher',
            server_stack=server_stack
        )
        ServersApi(
            self, 'Servers',
            resource=rest_api.root,
            user_pool=users.user_pool,
            user_client=users.user_client,
            user_pool_parameter=users.user_pool_parameter,
            launcher=launcher
        )
