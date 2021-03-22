from aws_cdk import (
    core as cdk,
    aws_apigateway as apigw
)


class Api(cdk.Construct):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.rest_api = apigw.RestApi(self, 'api')
