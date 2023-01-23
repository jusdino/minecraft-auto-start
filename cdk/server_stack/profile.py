from aws_cdk import Stack
from aws_cdk.aws_iam import Role, ServicePrincipal, PolicyDocument, PolicyStatement, Effect, CfnInstanceProfile
# We'll import the whole module here to dance around the massive module crushing IntelliJ
from aws_cdk import aws_ec2 as ec2
from aws_cdk.aws_s3 import Bucket
from constructs import Construct


class Profile(Construct):
    """
    A generic instance profile that has the AWS permissions needed by our minecraft servers
    """
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        vpc_name = self.node.try_get_context('vpc_name')
        vpc = ec2.Vpc.from_lookup(
            self, 'Vpc',
            vpc_name=vpc_name
        )
        hosted_zone_id = self.node.try_get_context('hosted_zone_id')
        server_subnet_id = vpc.public_subnets[0].subnet_id
        data_bucket = Bucket.from_bucket_name(
            self, 'DataBucket',
            bucket_name=self.node.try_get_context('data_bucket_id')
        )

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
                        f'arn:aws:route53:::hostedzone/{hosted_zone_id}'
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
                            'ec2:Subnet': f'arn:aws:ec2:{Stack.of(self).region}:{Stack.of(self).account}:subnet/{server_subnet_id}'
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
        data_bucket.grant_read_write(self.role)
        self.instance_profile = CfnInstanceProfile(
            self, 'InstanceProfile',
            roles=[self.role.role_name]
        )
        # self.instance_profile.add_dependency(self.role.node.default_child)
        # print(self.instance_profile.obtain_dependencies())
