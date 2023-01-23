from constructs import Construct
from aws_cdk import CfnOutput
from aws_cdk.aws_route53 import HostedZone, ARecord, RecordTarget
from aws_cdk.aws_route53_targets import ApiGateway
from aws_cdk.aws_apigateway import RestApi, DomainNameOptions, StageOptions
from aws_cdk.aws_certificatemanager import Certificate, CertificateValidation


class Api(Construct):
    """
    Create the root RestApi, configure ACM cert and Rout53 record mapping
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        environment = self.node.try_get_context('environment')
        server_domain = self.node.try_get_context('server_domain')
        hosted_zone_id = self.node.try_get_context('hosted_zone_id')

        if environment == 'prod':
            self.domain_name = f'start.{server_domain}'
        else:
            self.domain_name = f'start.{environment}.{server_domain}'

        hosted_zone = HostedZone.from_hosted_zone_attributes(
            self, 'Zone',
            hosted_zone_id=hosted_zone_id,
            zone_name=server_domain
        )
        certificate = Certificate(
            self, 'StartCert',
            domain_name=self.domain_name,
            validation=CertificateValidation.from_dns(hosted_zone=hosted_zone)
        )
        self.rest_api = RestApi(
            self, 'api',
            domain_name=DomainNameOptions(
                certificate=certificate,
                domain_name=self.domain_name
            ),
            deploy_options=StageOptions(
                stage_name=environment
            )
        )
        arecord = ARecord(
            self, 'StartARecord',
            zone=hosted_zone,
            record_name=self.domain_name,
            target=RecordTarget(
                alias_target=ApiGateway(self.rest_api)
            )
        )
        CfnOutput(self, 'DNSName', value=arecord.domain_name)
