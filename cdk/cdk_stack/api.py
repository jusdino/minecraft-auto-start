from aws_cdk import (
    core as cdk,
    aws_apigateway as apigw,
    aws_route53 as r53,
    aws_route53_targets as r53_targets,
    aws_certificatemanager as acm
)


class Api(cdk.Construct):
    """
    Create the root RestApi, configure ACM cert and Rout53 record mapping
    """

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        environment = self.node.try_get_context('environment')
        server_domain = self.node.try_get_context('server_domain')
        hosted_zone_id = self.node.try_get_context('hosted_zone_id')

        if environment == 'prod':
            self.domain_name = f'start.{server_domain}'
        else:
            self.domain_name = f'start.{environment}.{server_domain}'

        hosted_zone = r53.HostedZone.from_hosted_zone_attributes(
            self, 'Zone',
            hosted_zone_id=hosted_zone_id,
            zone_name=server_domain
        )
        certificate = acm.Certificate(
            self, 'StartCert',
            domain_name=self.domain_name,
            validation=acm.CertificateValidation.from_dns(hosted_zone=hosted_zone)
        )
        self.rest_api = apigw.RestApi(
            self, 'api',
            domain_name=apigw.DomainNameOptions(
                certificate=certificate,
                domain_name=self.domain_name
            ),
            deploy_options=apigw.StageOptions(
                stage_name=environment
            )
        )
        arecord = r53.ARecord(
            self, 'StartARecord',
            zone=hosted_zone,
            record_name=self.domain_name,
            target=r53.RecordTarget(
                alias_target=r53_targets.ApiGateway(self.rest_api)
            )
        )
        cdk.CfnOutput(self, 'DNSName', value=arecord.domain_name)
