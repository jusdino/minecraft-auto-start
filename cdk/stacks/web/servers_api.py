from aws_cdk.aws_logs import RetentionDays
from constructs import Construct
from aws_cdk import Duration
from aws_cdk.aws_lambda import Runtime
from aws_cdk.aws_lambda_python_alpha import PythonFunction
from aws_cdk.aws_apigateway import Resource, LambdaIntegration, MethodOptions, \
    AuthorizationType, CognitoUserPoolsAuthorizer

from stacks.persistent import PersistentStack


class ServersApi(Construct):

    def __init__(
            self, scope: Construct,
            construct_id: str,
            resource: Resource,
            persistent_stack: PersistentStack,
            launcher,
            **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        debug = 'true' if self.node.try_get_context('debug') is True else 'false'
        sub_domain = self.node.try_get_context('sub_domain')

        class ServerLambda(PythonFunction):
            def __init__(self, scope, construct_id, handler: str):
                super().__init__(
                    scope, construct_id,
                    entry='lambdas/servers',
                    index='handlers.py',
                    handler=handler,
                    runtime=Runtime.PYTHON_3_12,
                    log_retention=RetentionDays.ONE_MONTH,
                    timeout=Duration.seconds(30),
                    environment={
                        'DEBUG': debug,
                        'SUB_DOMAIN': sub_domain,
                        'DYNAMODB_SERVERS_TABLE_NAME': persistent_stack.servers_table.table_name,
                        'LAUNCHER_FUNCTION_ARN': launcher.function.function_arn
                    }
                )
                persistent_stack.servers_table.grant_read_write_data(self)
                persistent_stack.encryption_key.grant_encrypt_decrypt(self)
                launcher.function.grant_invoke(self)

        user_pool_parameter_lambda = PythonFunction(
            self, 'UserPoolParameterLambda',
            entry='lambdas/parameter',
            index='main.py',
            handler='main',
            log_retention=RetentionDays.ONE_MONTH,
            runtime=Runtime.PYTHON_3_12,
            timeout=Duration.seconds(30),
            environment={
                'USER_POOL_PARAMETER': persistent_stack.users.user_pool_parameter.parameter_name
            }
        )
        persistent_stack.users.user_pool_parameter.grant_read(user_pool_parameter_lambda)

        user_pool_authorizer = CognitoUserPoolsAuthorizer(
            self, 'UserPoolAuthorizer',
            cognito_user_pools=[persistent_stack.users.user_pool]
        )

        # /api
        api = resource.add_resource('api')

        # /api/user_pool
        parameter = api.add_resource('user_pool')
        parameter.add_method(
            'GET',
            integration=LambdaIntegration(user_pool_parameter_lambda),
            authorization_type=AuthorizationType.NONE
        )

        # GET /api/servers
        servers = api.add_resource('servers')
        servers.add_method(
            'GET',
            integration=LambdaIntegration(ServerLambda(
                self, 'GetServersFunction',
                handler='get_servers'
            )),
            authorizer=user_pool_authorizer
        )

        # GET /api/servers/{hostname}
        server = servers.add_resource('{hostname}')
        server.add_method(
            'GET',
            integration=LambdaIntegration(ServerLambda(
                self, 'GetOneServerFunction',
                handler='get_one_server'
            )),
            authorizer=user_pool_authorizer
        )

        # PUT /api/servers/{hostname}/launch
        server.add_resource('launch').add_method(
            'PUT',
            integration=LambdaIntegration(ServerLambda(
                self, 'LaunchServerFunction',
                handler='launch_server'
            )),
            authorizer=user_pool_authorizer
        )
