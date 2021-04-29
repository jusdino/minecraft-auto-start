from aws_cdk import (
    core as cdk,
    aws_kms as kms,
    aws_dynamodb as db,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_cognito as cognito,
    aws_ssm as ssm
)
from aws_cdk.aws_lambda_python import PythonFunction


class ServersApi(cdk.Construct):

    def __init__(
            self, scope: cdk.Construct,
            construct_id: str,
            context,
            resource: apigw.Resource,
            user_pool: cognito.UserPool,
            user_client: cognito.UserPoolClient,
            user_pool_parameter: ssm.StringParameter,
            **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        servers_table = db.Table.from_table_name(self, 'servers-dynamo', context['servers_table_name'])
        servers_key = kms.Key.from_key_arn(
            self, 'ServersKey',
            f'arn:aws:kms:{context["region"]}:{context["account_id"]}:key/{context["kms_key_id"]}')

        servers_lambda = PythonFunction(
            self, 'ServersLambda',
            entry='servers_lambda',
            index='views.py',
            handler='servers',
            runtime=_lambda.Runtime.PYTHON_3_8,
            timeout=cdk.Duration.seconds(30),
            environment={
                'DYNAMODB_SERVERS_TABLE_NAME': servers_table.table_name,
            }
        )
        servers_table.grant_read_write_data(servers_lambda)
        servers_key.grant_encrypt_decrypt(servers_lambda)

        server_lambda = PythonFunction(
            self, 'ServerLambda',
            entry='servers_lambda',
            index='views.py',
            handler='server',
            runtime=_lambda.Runtime.PYTHON_3_8,
            timeout=cdk.Duration.seconds(30),
            environment={
                'DYNAMODB_SERVERS_TABLE_NAME': servers_table.table_name
            }
        )
        servers_table.grant_read_write_data(server_lambda)
        servers_key.grant_encrypt_decrypt(server_lambda)

        user_pool_parameter_lambda = PythonFunction(
            self, 'UserPoolParameterLambda',
            entry='parameter_lambda',
            index='main.py',
            handler='main',
            runtime=_lambda.Runtime.PYTHON_3_8,
            timeout=cdk.Duration.seconds(30),
            environment={
                'USER_POOL_PARAMETER': user_pool_parameter.parameter_name
            }
        )
        user_pool_parameter.grant_read(user_pool_parameter_lambda)

        user_pool_authorizer = apigw.CognitoUserPoolsAuthorizer(
            self, 'UserPoolAuthorizer',
            cognito_user_pools = [user_pool]
        )

        # /api
        api = resource.add_resource('api')

        # /api/user_pool
        parameter = api.add_resource(
            'user_pool',
            default_integration=apigw.LambdaIntegration(user_pool_parameter_lambda),
            default_method_options=apigw.MethodOptions(authorization_type=apigw.AuthorizationType.NONE)
        )
        parameter.add_method('GET')
    
        # /api/servers
        servers = api.add_resource(
            'servers',
            default_integration=apigw.LambdaIntegration(servers_lambda),
            default_method_options=apigw.MethodOptions(authorizer=user_pool_authorizer)
        )
        servers.add_method('GET')
        servers.add_method('PUT')

        # /api/servers/{hostname}
        server = servers.add_resource(
            '{hostname}',
            default_integration=apigw.LambdaIntegration(server_lambda),
            default_method_options=apigw.MethodOptions(authorizer=user_pool_authorizer)
        )
        server.add_method('GET')
        server.add_method('POST')
