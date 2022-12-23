from constructs import Construct
from aws_cdk import Duration
from aws_cdk.aws_kms import Key
from aws_cdk.aws_cognito import UserPool, UserPoolClient
from aws_cdk.aws_dynamodb import Table
from aws_cdk.aws_lambda import Runtime
from aws_cdk.aws_ssm import StringParameter
from aws_cdk.aws_ecs import Cluster, ITaskDefinition
from aws_cdk.aws_lambda_python_alpha import PythonFunction
from aws_cdk.aws_apigateway import Resource, LambdaIntegration, MethodOptions, AuthorizationType, CognitoUserPoolsAuthorizer

from .launcher import GrantingTaskDefinition


class ServersApi(Construct):

    def __init__(
            self, scope: Construct,
            construct_id: str,
            context,
            resource: Resource,
            user_pool: UserPool,
            user_client: UserPoolClient,
            user_pool_parameter: StringParameter,
            launcher_network_config_parameter: StringParameter,
            launcher_task_definition: GrantingTaskDefinition,
            launcher_cluster: Cluster,
            **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        server_domain = self.node.try_get_context('server_domain')

        servers_table = Table.from_table_name(self, 'servers-dynamo', context['servers_table_name'])
        servers_key = Key.from_key_arn(
            self, 'ServersKey',
            f'arn:aws:kms:{context["region"]}:{context["account_id"]}:key/{context["kms_key_id"]}'
        )

        class ServerLambda(PythonFunction):
            def __init__(self, scope, construct_id, handler: str):
                super().__init__(
                    scope, construct_id,
                    entry='servers_lambda',
                    index='views.py',
                    handler=handler,
                    runtime=Runtime.PYTHON_3_8,
                    timeout=Duration.seconds(30),
                    environment={
                        'SERVER_DOMAIN': server_domain,
                        'DYNAMODB_SERVERS_TABLE_NAME': servers_table.table_name,
                        'LAUNCHER_NETWORK_CONFIG_PARAMETER': launcher_network_config_parameter.parameter_name,
                        'LAUNCHER_TASK_ARN': launcher_task_definition.task_definition_arn,
                        'CLUSTER_ARN': launcher_cluster.cluster_arn
                    }
                )
                servers_table.grant_read_write_data(self)
                servers_key.grant_encrypt_decrypt(self)
                launcher_network_config_parameter.grant_read(self)
                launcher_task_definition.grant_run(self)


        servers_lambda = ServerLambda(self, 'ServersLambda', handler='servers')
        server_lambda = ServerLambda(self, 'ServerLambda', handler='server')

        user_pool_parameter_lambda = PythonFunction(
            self, 'UserPoolParameterLambda',
            entry='parameter_lambda',
            index='main.py',
            handler='main',
            runtime=Runtime.PYTHON_3_8,
            timeout=Duration.seconds(30),
            environment={
                'USER_POOL_PARAMETER': user_pool_parameter.parameter_name
            }
        )
        user_pool_parameter.grant_read(user_pool_parameter_lambda)

        user_pool_authorizer = CognitoUserPoolsAuthorizer(
            self, 'UserPoolAuthorizer',
            cognito_user_pools = [user_pool]
        )

        # /api
        api = resource.add_resource('api')

        # /api/user_pool
        parameter = api.add_resource(
            'user_pool',
            default_integration=LambdaIntegration(user_pool_parameter_lambda),
            default_method_options=MethodOptions(authorization_type=AuthorizationType.NONE)
        )
        parameter.add_method('GET')
    
        # /api/servers
        servers = api.add_resource(
            'servers',
            default_integration=LambdaIntegration(servers_lambda),
            default_method_options=MethodOptions(authorizer=user_pool_authorizer)
        )
        servers.add_method('GET')
        servers.add_method('PUT')

        # /api/servers/{hostname}
        server = servers.add_resource(
            '{hostname}',
            default_integration=LambdaIntegration(server_lambda),
            default_method_options=MethodOptions(authorizer=user_pool_authorizer)
        )
        server.add_method('GET')
        server.add_method('PUT')
        server.add_method('POST')
