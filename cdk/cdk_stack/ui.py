from aws_cdk import (
    core as cdk,
    aws_s3 as s3,
    aws_iam as iam,
    aws_s3_deployment as s3_deployment,
    aws_apigateway as apigw
)
from aws_cdk.aws_lambda_python import PythonFunction


class ServersUi(cdk.Construct):
    """
    Add a /ui/ endpoint to the provided Resource that serves static content from an s3 bucket
    """

    def __init__(self, scope: cdk.Construct, construct_id: str, rest_api: apigw.Resource, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        asset_bucket = s3.Bucket(
            self, 'AssetBucket',
            website_index_document='index.html',
            public_read_access=True,
            removal_policy=cdk.RemovalPolicy.DESTROY
        )
        s3_deployment.BucketDeployment(
            self, 'BucketDeployment',
            sources=[s3_deployment.Source.asset('ui-static')],
            destination_bucket=asset_bucket,
            retain_on_delete=False
        )
        cdk.CfnOutput(self, 'BucketDomain', value=asset_bucket.bucket_website_domain_name)
        s3_integration_role = iam.Role(
            self, 'AwsIntegrationRole',
            assumed_by=iam.ServicePrincipal(service='apigateway.amazonaws.com')
        )
        asset_bucket.grant_read(s3_integration_role)
        self.ui_resource = self._add_get_integration(rest_api, asset_bucket, s3_integration_role)
        self._add_item_integration(self.ui_resource, asset_bucket, s3_integration_role)
    
    def _add_get_integration(self, rest_api: apigw.Resource, asset_bucket, s3_integration_role) -> apigw.Resource:
        """
        Add integration for /ui/
        """
        s3_integration = apigw.AwsIntegration(
            service='s3',
            path=f'{asset_bucket.bucket_name}/index.html',
            integration_http_method='GET',
            options=apigw.IntegrationOptions(
                credentials_role=s3_integration_role,
                integration_responses=[
                    apigw.IntegrationResponse(
                        status_code='200',
                        response_parameters={
                            'method.response.header.Content-Type': 'integration.response.header.Content-Type',
                            'method.response.header.Content-Length': 'integration.response.header.Content-Length',
                            'method.response.header.Timestamp': 'integration.response.header.Date'
                        }
                    ),
                    apigw.IntegrationResponse(
                        status_code='400',
                        selection_pattern=r'4\d{2}',
                        response_parameters={
                            'method.response.header.Content-Type': 'integration.response.header.Content-Type',
                            'method.response.header.Content-Length': 'integration.response.header.Content-Length'
                        }
                    ),
                    apigw.IntegrationResponse(
                        status_code='500',
                        selection_pattern=r'5\d{2}',
                        response_parameters={
                            'method.response.header.Content-Type': 'integration.response.header.Content-Type',
                            'method.response.header.Content-Length': 'integration.response.header.Content-Length'
                        }
                    )
                ]
            )
        )
        ui = rest_api.add_resource('ui')
        ui.add_method('GET', integration=s3_integration, method_responses=[
                apigw.MethodResponse(
                    status_code='200',
                    response_parameters={
                        'method.response.header.Content-Type': True,
                        'method.response.header.Content-Length': True,
                        'method.response.header.Timestamp': True
                    }
                ),
                apigw.MethodResponse(status_code='400',
                    response_parameters={
                        'method.response.header.Content-Type': True,
                        'method.response.header.Content-Length': True
                    }
                ),
                apigw.MethodResponse(status_code='500',
                    response_parameters={
                        'method.response.header.Content-Type': True,
                        'method.response.header.Content-Length': True
                    }
                )
            ]
        )
        return ui

    def _add_item_integration(self, ui_resource: apigw.Resource, asset_bucket, s3_integration_role) -> apigw.Resource:
        """
        Add integration for /ui/{object}
        """
        s3_integration = apigw.AwsIntegration(
            service='s3',
            path=f'{asset_bucket.bucket_name}/{{object}}',
            integration_http_method='GET',
            options=apigw.IntegrationOptions(
                credentials_role=s3_integration_role,
                integration_responses=[
                    apigw.IntegrationResponse(
                        status_code='200',
                        response_parameters={
                            'method.response.header.Content-Type': 'integration.response.header.Content-Type',
                            'method.response.header.Content-Length': 'integration.response.header.Content-Length',
                            'method.response.header.Timestamp': 'integration.response.header.Date'
                        }
                    ),
                    apigw.IntegrationResponse(
                        status_code='400',
                        selection_pattern=r'4\d{2}',
                        response_parameters={
                            'method.response.header.Content-Type': 'integration.response.header.Content-Type',
                            'method.response.header.Content-Length': 'integration.response.header.Content-Length'
                        }
                    ),
                    apigw.IntegrationResponse(
                        status_code='500',
                        selection_pattern=r'5\d{2}',
                        response_parameters={
                            'method.response.header.Content-Type': 'integration.response.header.Content-Type',
                            'method.response.header.Content-Length': 'integration.response.header.Content-Length'
                        }
                    )
                ],
                request_parameters={
                    'integration.request.path.object': 'method.request.path.item'
                }
            )
        )
        ui_item = ui_resource.add_resource('{item}')
        ui_item.add_method(
            'GET',
            integration=s3_integration,
            method_responses=[
                apigw.MethodResponse(
                    status_code='200',
                    response_parameters={
                        'method.response.header.Content-Type': True,
                        'method.response.header.Content-Length': True,
                        'method.response.header.Timestamp': True
                    }
                ),
                apigw.MethodResponse(status_code='400',
                    response_parameters={
                        'method.response.header.Content-Type': True,
                        'method.response.header.Content-Length': True
                    }
                ),
                apigw.MethodResponse(status_code='500',
                    response_parameters={
                        'method.response.header.Content-Type': True,
                        'method.response.header.Content-Length': True
                    }
                )
            ],
            request_parameters={
                'method.request.path.item': True
            }
        )
        return ui_item
