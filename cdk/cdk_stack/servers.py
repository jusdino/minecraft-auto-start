from aws_cdk import (
    core as cdk,
    aws_kms as kms,
    aws_dynamodb as db,
    aws_lambda as _lambda,
    aws_apigateway as apigw
)
from aws_cdk.aws_lambda_python import PythonFunction


class ServersApi(cdk.Construct):

    def __init__(self, scope: cdk.Construct, construct_id: str, context, resource: apigw.Resource, **kwargs) -> None:
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
                'DYNAMODB_SERVERS_TABLE_NAME': servers_table.table_name
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

        # /api
        api = resource.add_resource('api')
    
        # /api/servers
        servers = api.add_resource('servers', default_integration=apigw.LambdaIntegration(servers_lambda))
        servers.add_method('GET')
        servers.add_method('PUT')

        # /api/servers/{hostname}
        server = servers.add_resource('{hostname}', default_integration=apigw.LambdaIntegration(server_lambda))
        server.add_method('GET')
        server.add_method('POST')
