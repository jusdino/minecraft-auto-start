import os
from unittest import TestCase
from unittest.mock import MagicMock

from aws_lambda_powertools.utilities.typing import LambdaContext
from moto import mock_aws


@mock_aws
class BaseTestMAS(TestCase):
    """
    Mock out required env vars then import config so our unit tests
    don't have any particular environmental variable dependencies.
    """
    def setUp(self):
        super().setUp()
        env_vars = {
            'DEBUG': 'true',
            'AWS_DEFAULT_REGION': 'us-west-1',
            'APP_NAME': 'launcher',
            'SUB_DOMAIN': 'example.org',
            'DYNAMODB_SERVERS_TABLE_NAME': 'servers-table',
            'LAUNCHER_FUNCTION_ARN': 'arn:aws:stuff:like:an/arn'
        }
        os.environ.update(env_vars)
        self.build_resources()
        self.addCleanup(self.destroy_resources)

        self.mock_context = MagicMock(spec=LambdaContext)

    def build_resources(self):
        import boto3

        dynamodb = boto3.resource('dynamodb')
        self.table = dynamodb.create_table(
            TableName='servers-table',
            AttributeDefinitions=[{
                'AttributeName': 'hostname',
                'AttributeType': 'S'
            }],
            KeySchema=[{
                'AttributeName': 'hostname',
                'KeyType': 'HASH'
            }],
            BillingMode='PAY_PER_REQUEST'
        )

    def destroy_resources(self):
        self.table.delete()
