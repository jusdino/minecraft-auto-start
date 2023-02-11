from aws_cdk import Stack
from aws_cdk.aws_iam import Role, ServicePrincipal, PolicyDocument, PolicyStatement, Effect, CfnInstanceProfile
from constructs import Construct

from persistent_stack import PersistentStack
from server_stack import Networking


class Profile(Construct):
    """
    A generic instance profile that has the AWS permissions needed by our minecraft servers
    """
    def __init__(self, scope: Construct, construct_id: str, persistent_stack: PersistentStack, networking: Networking, **kwargs) -> None:
        super().__init__(scope, construct_id)
        hosted_zone_id = scope.node.try_get_context('hosted_zone_id')

        # We'll add some direct IAM permissions for ec2 stuff that isn't covered by cdk
        policy_doc = PolicyDocument(
            statements=[
                # Allow role to update DNS records where we expect them
                PolicyStatement(
                    effect=Effect.ALLOW,
                    actions=[
                        'route53:ChangeResourceRecordSets',
                        'route53:GetChange',
                        'route53:ListResourceRecordSets'
                    ],
                    resources=[
                        f'arn:{Stack.of(self).partition}:route53:::hostedzone/{hosted_zone_id}'
                    ],
                    conditions={
                        'StringEquals': {'route53:ChangeResourceRecordSetsRecordTypes': ['A']}
                    }
                ),
                # Allow function to associate elastic ip addresses
                PolicyStatement(
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
                            'ec2:Subnet': f'arn:{Stack.of(self).partition}:ec2:{Stack.of(self).region}:{Stack.of(self).account}:subnet/{networking.subnet.subnet_id}'
                        },
                    }
                )
            ]
        )
        self.role = Role(
            self, 'Role',
            assumed_by=ServicePrincipal('ec2.amazonaws.com'),
            inline_policies={'default-policy': policy_doc}
        )
        persistent_stack.encryption_key.grant_encrypt_decrypt(self.role)
        persistent_stack.data_bucket.grant_read_write(self.role)
        self.instance_profile = CfnInstanceProfile(
            self, 'InstanceProfile',
            roles=[self.role.role_name]
        )
