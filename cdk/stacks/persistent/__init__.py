from aws_cdk import Stack, RemovalPolicy, CfnOutput
from aws_cdk.aws_dynamodb import Table, BillingMode, Attribute, AttributeType, TableEncryption
from aws_cdk.aws_kms import Key
from aws_cdk.aws_s3 import Bucket, BlockPublicAccess, BucketEncryption
from constructs import Construct

from .users import Users


class PersistentStack(Stack):
    """
    The Stack housing data and resources that are intended to be more long-lived.
    """

    def __init__(self, scope: Construct, construct_id: str, *, api_domain_name: str, sub_domain: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        environment = self.node.get_context('environment')
        # Only set removal policies to RETAIN for prod
        removal = RemovalPolicy.RETAIN if environment == 'prod' else RemovalPolicy.DESTROY

        self.encryption_key = Key(
            self, 'EncryptionKey',
            removal_policy=removal
        )

        self.users = Users(
            self, 'Users',
            domain_name=api_domain_name,
            removal=removal
        )

        # Note: Normally it's a good idea to avoid forcing resource names in CloudFormation
        # but in this case, since I'm frequently interacting with data in this bucket manually,
        # I want it to be a convenient name
        bucket_name = f'mas-{sub_domain.replace(".", "-")}-data'
        self.data_bucket = Bucket(
            self, 'Data',
            bucket_name=bucket_name,
            block_public_access=BlockPublicAccess.BLOCK_ALL,
            removal_policy=removal,
            versioned=environment == 'prod',
            encryption=BucketEncryption.KMS,
            encryption_key=self.encryption_key,
            auto_delete_objects=removal == RemovalPolicy.DESTROY
        )

        self.servers_table = Table(
            self, 'ServersTable',
            billing_mode=BillingMode.PAY_PER_REQUEST,
            partition_key=Attribute(name='hostname', type=AttributeType.STRING),
            encryption=TableEncryption.CUSTOMER_MANAGED,
            encryption_key=self.encryption_key,
            removal_policy=removal
        )

        CfnOutput(
            self, 'DataBucketName',
            value=self.data_bucket.bucket_name
        )
