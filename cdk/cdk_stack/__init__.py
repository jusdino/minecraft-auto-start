from aws_cdk import (
    core as cdk,
    aws_kms as kms,
    aws_dynamodb as db,
    aws_lambda as _lambda,
    aws_apigateway as apigw
)
from aws_cdk.aws_lambda_python import PythonFunction

from .api import Api
from .servers import ServersApi
from .ui import ServersUi
from .auth import CognitoStack


class CdkStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, context: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        rest_api = Api(self, 'Api').rest_api
        ServersApi(self, 'Servers', context, resource=rest_api.root)
        ServersUi(self, 'UI', rest_api=rest_api.root)
        CognitoStack(self, 'Users')
