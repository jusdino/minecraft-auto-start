from constructs import Construct
from aws_cdk import Stack

from .api import Api
from .servers import ServersApi
from .ui import ServersUi
from .users import Users
from .launcher import Launcher


class CdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, context: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        rest_api = Api(self, 'Api').rest_api
        ServersUi(self, 'UI', rest_api=rest_api.root)
        users = Users(
            self, 'Users',
            domain_name=rest_api.domain_name.domain_name
        )
        launcher = Launcher(
            self, 'Launcher'
        )
        ServersApi(
            self, 'Servers',
            context,
            resource=rest_api.root,
            user_pool=users.user_pool,
            user_client=users.user_client,
            user_pool_parameter=users.user_pool_parameter,
            launcher_network_config_parameter=launcher.network_config_parameter,
            launcher_cluster=launcher.cluster,
            launcher_task_definition=launcher.task_definition
        )
