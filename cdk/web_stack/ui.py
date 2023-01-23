from constructs import Construct
from aws_cdk import RemovalPolicy, CfnOutput
from aws_cdk.aws_iam import Role, ServicePrincipal
from aws_cdk.aws_s3 import Bucket
from aws_cdk.aws_s3_deployment import BucketDeployment, Source
from aws_cdk.aws_apigateway import Resource, AwsIntegration, IntegrationOptions, IntegrationResponse, MethodResponse


class ServersUi(Construct):
    """
    Add a /ui/ endpoint to the provided Resource that serves static content from an s3 bucket
    """

    def __init__(self, scope: Construct, construct_id: str, rest_api: Resource, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        asset_bucket = Bucket(
            self, 'AssetBucket',
            website_index_document='index.html',
            public_read_access=True,
            removal_policy=RemovalPolicy.DESTROY
        )
        BucketDeployment(
            self, 'BucketDeployment',
            sources=[Source.asset('ui-static')],
            destination_bucket=asset_bucket,
            retain_on_delete=False
        )
        CfnOutput(self, 'BucketDomain', value=asset_bucket.bucket_website_domain_name)
        s3_integration_role = Role(
            self, 'AwsIntegrationRole',
            assumed_by=ServicePrincipal(service='apigateway.amazonaws.com')
        )
        asset_bucket.grant_read(s3_integration_role)
        self.ui_resource = self._add_get_integration(rest_api, asset_bucket, s3_integration_role)
        self._add_item_integration(self.ui_resource, asset_bucket, s3_integration_role)
    
    def _add_get_integration(self, rest_api: Resource, asset_bucket, s3_integration_role) -> Resource:
        """
        Add integration for /ui/
        """
        s3_integration = AwsIntegration(
            service='s3',
            path=f'{asset_bucket.bucket_name}/index.html',
            integration_http_method='GET',
            options=IntegrationOptions(
                credentials_role=s3_integration_role,
                integration_responses=[
                    IntegrationResponse(
                        status_code='200',
                        response_parameters={
                            'method.response.header.Content-Type': 'integration.response.header.Content-Type',
                            'method.response.header.Content-Length': 'integration.response.header.Content-Length',
                            'method.response.header.Timestamp': 'integration.response.header.Date'
                        }
                    ),
                    IntegrationResponse(
                        status_code='400',
                        selection_pattern=r'4\d{2}',
                        response_parameters={
                            'method.response.header.Content-Type': 'integration.response.header.Content-Type',
                            'method.response.header.Content-Length': 'integration.response.header.Content-Length'
                        }
                    ),
                    IntegrationResponse(
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
                MethodResponse(
                    status_code='200',
                    response_parameters={
                        'method.response.header.Content-Type': True,
                        'method.response.header.Content-Length': True,
                        'method.response.header.Timestamp': True
                    }
                ),
                MethodResponse(status_code='400',
                    response_parameters={
                        'method.response.header.Content-Type': True,
                        'method.response.header.Content-Length': True
                    }
                ),
                MethodResponse(status_code='500',
                    response_parameters={
                        'method.response.header.Content-Type': True,
                        'method.response.header.Content-Length': True
                    }
                )
            ]
        )
        return ui

    def _add_item_integration(self, ui_resource: Resource, asset_bucket, s3_integration_role) -> Resource:
        """
        Add integration for /ui/{object}
        """
        s3_integration = AwsIntegration(
            service='s3',
            path=f'{asset_bucket.bucket_name}/{{object}}',
            integration_http_method='GET',
            options=IntegrationOptions(
                credentials_role=s3_integration_role,
                integration_responses=[
                    IntegrationResponse(
                        status_code='200',
                        response_parameters={
                            'method.response.header.Content-Type': 'integration.response.header.Content-Type',
                            'method.response.header.Content-Length': 'integration.response.header.Content-Length',
                            'method.response.header.Timestamp': 'integration.response.header.Date'
                        }
                    ),
                    IntegrationResponse(
                        status_code='400',
                        selection_pattern=r'4\d{2}',
                        response_parameters={
                            'method.response.header.Content-Type': 'integration.response.header.Content-Type',
                            'method.response.header.Content-Length': 'integration.response.header.Content-Length'
                        }
                    ),
                    IntegrationResponse(
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
                MethodResponse(
                    status_code='200',
                    response_parameters={
                        'method.response.header.Content-Type': True,
                        'method.response.header.Content-Length': True,
                        'method.response.header.Timestamp': True
                    }
                ),
                MethodResponse(status_code='400',
                    response_parameters={
                        'method.response.header.Content-Type': True,
                        'method.response.header.Content-Length': True
                    }
                ),
                MethodResponse(status_code='500',
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
