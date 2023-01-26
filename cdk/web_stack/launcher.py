import json

from aws_cdk import Duration, Stack
from aws_cdk.aws_lambda import Runtime
from aws_cdk.aws_lambda_python_alpha import PythonFunction
from constructs import Construct
from aws_cdk.aws_iam import PolicyStatement, Effect
# We'll import the whole module here to dance around the massive module crushing IntelliJ
from aws_cdk import aws_ec2 as ec2

from persistent_stack import PersistentStack
from server_stack import ServerStack


class Launcher(Construct):
    """
    Just look up existing resources until we migrate them to CDK
    """

    def __init__(self, scope: Construct, construct_id: str, *,
                 domain_name: str,
                 server_stack: ServerStack,
                 persistent_stack: PersistentStack,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        debug = 'true' if self.node.try_get_context('debug') is True else 'false'
        environment_name = self.node.try_get_context('environment')
        hosted_zone_id = self.node.try_get_context('hosted_zone_id')
        server_security_group_id = self.node.try_get_context('server_security_group_id')
        key_pair_name = self.node.try_get_context('key_pair_name')
        vpc_name = self.node.try_get_context('vpc_name')
        vpc = ec2.Vpc.from_lookup(
            self, 'Vpc',
            vpc_name=vpc_name
        )

        server_subnet_id = vpc.public_subnets[0].subnet_id
        server_tags = [
            {
                'Key': 'environment',
                'Value': environment_name
            }
        ]
        self.function = PythonFunction(
            self, 'LauncherFunction',
            entry='launcher_lambda',
            index='main.py',
            handler='main',
            runtime=Runtime.PYTHON_3_8,
            timeout=Duration.seconds(30),
            environment={
                'DEBUG': debug,
                'TAGS': json.dumps(server_tags),
                'SSH_KEY_NAME': key_pair_name,
                'DATA_BUCKET_ID': persistent_stack.data_bucket.bucket_name,
                'HOSTED_ZONE_ID': hosted_zone_id,
                'HOSTED_ZONE_NAME': domain_name,
                'SECURITY_GROUP_ID': server_security_group_id,
                'SUBNET_ID': server_subnet_id,
                'INSTANCE_PROFILE_ARN': server_stack.profile.instance_profile.attr_arn
            }
        )
        server_stack.profile.role.grant_pass_role(self.function)
        # Allow function to get public aws parameters
        self.function.add_to_role_policy(PolicyStatement(
            effect=Effect.ALLOW,
            actions=['ssm:GetParameter'],
            resources=['arn:aws:ssm:*:*:parameter/aws/*']
        ))
        # Allow function to describe ec2 resources
        self.function.add_to_role_policy(PolicyStatement(
            effect=Effect.ALLOW,
            actions=['ec2:Describe*'],
            resources=['*']
        ))
        # Allow function to launch instances where we expect them
        self.function.add_to_role_policy(PolicyStatement(
            effect=Effect.ALLOW,
            actions=[
                'ec2:RunInstances',
                'ec2:CreateTags'
            ],
            resources=[
                f'arn:aws:ec2:*:*:subnet/{server_subnet_id}',
                'arn:aws:ec2:*:*:network-interface/*',
                'arn:aws:ec2:*:*:instance/*',
                'arn:aws:ec2:*:*:volume/*',
                'arn:aws:ec2:*::image/ami-*',
                f'arn:aws:ec2:*:*:key-pair/{key_pair_name}',
                f'arn:aws:ec2:*:*:security-group/{server_security_group_id}'
            ]
        ))
        # Allow function to update DNS records where we expect them
        self.function.add_to_role_policy(PolicyStatement(
            effect=Effect.ALLOW,
            actions=[
                'route53:ChangeResourceRecordSets',
                'route53:GetChange',
                'route53:ListResourceRecordSets'
            ],
            resources=[
                f'arn:aws:route53:::hostedzone/{hosted_zone_id}'
            ],
            conditions={
                'StringEquals': {'route53:ChangeResourceRecordSetsRecordTypes': ['A']}
            }
        ))
        # Allow function to allocate elastic ip addresses
        self.function.add_to_role_policy(PolicyStatement(
            effect=Effect.ALLOW,
            actions=[
                'ec2:AllocateAddress',
                'ec2:CreateTags'
            ],
            resources=[f'arn:aws:ec2:{Stack.of(self).region}:*:elastic-ip/*']
        ))
        # Allow function to associate elastic ip addresses
        self.function.add_to_role_policy(PolicyStatement(
            effect=Effect.ALLOW,
            actions=[
                'ec2:AssociateAddress',
                'ec2:DescribeAddresses',
                'ec2:DisassociateAddress',
                'ec2:ReleaseAddress'
            ],
            resources=['*'],
            conditions={
                'StringEqualsIfExists': {
                    'ec2:Subnet': f'arn:aws:ec2:{Stack.of(self).region}:{Stack.of(self).account}:subnet/{server_subnet_id}'
                },
            }
        ))
