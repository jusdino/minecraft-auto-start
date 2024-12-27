import os
from aws_cdk.aws_logs import RetentionDays
from constructs import Construct
from aws_cdk import RemovalPolicy, CfnOutput
from aws_cdk.aws_iam import Role, ServicePrincipal
from aws_cdk.aws_s3 import Bucket, BlockPublicAccess
from aws_cdk.aws_s3_deployment import BucketDeployment, Source
from aws_cdk.aws_apigateway import Resource, AwsIntegration, HttpIntegration, IntegrationOptions, IntegrationResponse, MethodResponse


class ServersUi(Construct):
    """
    Add a /ui/ endpoint to the provided Resource that serves static content from an s3 bucket
    """

    def __init__(self, scope: Construct, construct_id: str, rest_api: Resource, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        asset_bucket = Bucket(
            self, 'AssetBucket',
            website_index_document='index.html',
            website_error_document='index.html',
            public_read_access=True,
            block_public_access=BlockPublicAccess.BLOCK_ACLS,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )
        BucketDeployment(
            self, 'BucketDeployment',
            sources=[Source.asset(os.path.join('ui-static', 'browser'))],
            destination_bucket=asset_bucket,
            log_retention=RetentionDays.ONE_MONTH,
            retain_on_delete=False
        )
        CfnOutput(self, 'BucketDomain', value=asset_bucket.bucket_website_domain_name)
        self.ui_resource = self._add_get_integration(rest_api, asset_bucket)
        self._add_proxy_integration(self.ui_resource, asset_bucket)

    def _add_get_integration(self, rest_api: Resource, asset_bucket) -> Resource:
        """
        Add integration for /ui/
        """
        http_integration = HttpIntegration(
            http_method='GET',
            url=f'{asset_bucket.bucket_website_url}/index.html',
            options=IntegrationOptions(
                integration_responses=[
                    IntegrationResponse(
                        status_code='200',
                        response_parameters={
                            'method.response.header.Content-Type': 'integration.response.header.Content-Type',
                            'method.response.header.Content-Length': 'integration.response.header.Content-Length',
                            'method.response.header.Timestamp': 'integration.response.header.Date'
                        }
                    ),
                    # We're specifically overriding 4XX responses with 200 so we can take advantage of
                    # our s3's error document being index.html
                    IntegrationResponse(
                        status_code='200',
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
        ui.add_method('GET', integration=http_integration, method_responses=[
                MethodResponse(
                    status_code='200',
                    response_parameters={
                        'method.response.header.Content-Type': True,
                        'method.response.header.Content-Length': True,
                        'method.response.header.Timestamp': True
                    }
                ),
                MethodResponse(
                    status_code='400',
                    response_parameters={
                        'method.response.header.Content-Type': True,
                        'method.response.header.Content-Length': True
                    }
                ),
                MethodResponse(
                    status_code='500',
                    response_parameters={
                        'method.response.header.Content-Type': True,
                        'method.response.header.Content-Length': True
                    }
                )
            ]
        )
        return ui

    def _add_proxy_integration(self, ui_resource: Resource, asset_bucket: Bucket) -> Resource:
        """
        Add integration for /ui/{proxy+}
        """
        http_integration = HttpIntegration(
            http_method='GET',
            url=f'{asset_bucket.bucket_website_url}/{{proxy}}',
            options=IntegrationOptions(
                integration_responses=[
                    IntegrationResponse(
                        status_code='200',
                        response_parameters={
                            'method.response.header.Content-Type': 'integration.response.header.Content-Type',
                            'method.response.header.Content-Length': 'integration.response.header.Content-Length',
                            'method.response.header.Timestamp': 'integration.response.header.Date'
                        }
                    ),
                    # We're specifically overriding 4XX responses with 200 so we can take advantage of
                    # our s3's error document being index.html
                    IntegrationResponse(
                        status_code='200',
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
                    'integration.request.path.proxy': 'method.request.path.proxy'
                }
            )
        )
        ui_item = ui_resource.add_resource('{proxy+}')
        ui_item.add_method(
            'GET',
            integration=http_integration,
            method_responses=[
                MethodResponse(
                    status_code='200',
                    response_parameters={
                        'method.response.header.Content-Type': True,
                        'method.response.header.Content-Length': True,
                        'method.response.header.Timestamp': True
                    }
                ),
                MethodResponse(
                    status_code='400',
                    response_parameters={
                        'method.response.header.Content-Type': True,
                        'method.response.header.Content-Length': True
                    }
                ),
                MethodResponse(
                    status_code='500',
                    response_parameters={
                        'method.response.header.Content-Type': True,
                        'method.response.header.Content-Length': True
                    }
                )
            ],
            request_parameters={
                'method.request.path.proxy': True
            }
        )
        return ui_item
