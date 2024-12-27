from constructs import Construct
from aws_cdk import Stack

from stacks.persistent import PersistentStack
from stacks.server import ServerStack
from .api import Api
from .servers_api import ServersApi
from .ui import ServersUi
from .launcher import Launcher


class WebStack(Stack):

    def __init__(self,
                 scope: Construct,
                 construct_id: str,
                 api_domain_name: str,
                 sub_domain: str,
                 server_stack: ServerStack,
                 persistent_stack: PersistentStack,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        rest_api = Api(self, 'Api', api_domain_name=api_domain_name).rest_api
        ServersUi(self, 'UI', rest_api=rest_api.root)
        launcher = Launcher(
            self, 'Launcher',
            server_stack=server_stack,
            persistent_stack=persistent_stack,
            sub_domain=sub_domain
        )
        ServersApi(
            self, 'Servers',
            resource=rest_api.root,
            persistent_stack=persistent_stack,
            launcher=launcher
        )
