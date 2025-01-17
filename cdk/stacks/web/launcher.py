import json

from aws_cdk import Duration, Stack
from aws_cdk.aws_lambda import Runtime
from aws_cdk.aws_lambda_python_alpha import PythonFunction
from aws_cdk.aws_logs import RetentionDays
from constructs import Construct
from aws_cdk.aws_iam import PolicyStatement, Effect

from stacks.persistent import PersistentStack
from stacks.server import ServerStack


class Launcher(Construct):
    """
    Function and permissions to launch a Minecraft server on EC2.
    """

    def __init__(self, scope: Construct, construct_id: str, *,
                 sub_domain: str,
                 server_stack: ServerStack,
                 persistent_stack: PersistentStack,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        debug = 'true' if self.node.try_get_context('debug') is True else 'false'
        environment_name = self.node.try_get_context('environment')
        hosted_zone_id = self.node.try_get_context('hosted_zone_id')
        key_pair_name = server_stack.key_pair.key_name

        server_subnet_id = server_stack.networking.subnet.subnet_id
        server_tags = [
            {
                'Key': 'Environment',
                'Value': environment_name
            }
        ]
        self.function = PythonFunction(
            self, 'LauncherFunction',
            entry='lambdas/launcher',
            index='main.py',
            handler='main',
            runtime=Runtime.PYTHON_3_12,
            timeout=Duration.seconds(30),
            log_retention=RetentionDays.ONE_MONTH,
            environment={
                'DEBUG': debug,
                'ENV': environment_name,
                'TAGS': json.dumps(server_tags),
                'SSH_KEY_NAME': server_stack.key_pair.key_name,
                'DATA_BUCKET_ID': persistent_stack.data_bucket.bucket_name,
                'HOSTED_ZONE_ID': hosted_zone_id,
                'SUB_DOMAIN': sub_domain,
                'SECURITY_GROUP_ID': server_stack.networking.security_group.security_group_id,
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
                f'arn:aws:ec2:*:*:security-group/{server_stack.networking.security_group.security_group_id}'
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
                    'ec2:Subnet':
                        f'arn:aws:ec2:{Stack.of(self).region}:'
                        f'{Stack.of(self).account}:subnet/{server_subnet_id}'
                },
            }
        ))
