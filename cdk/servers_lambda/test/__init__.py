import os
from unittest import TestCase, main
from unittest.mock import patch

import moto

# Just mock these globally once and for all
mock_dynamo = moto.mock_dynamodb()
mock_dynamo.start()


class BaseTestMAS(TestCase):
    """
    Mock out required env vars then import config so our unit tests
    don't have any particular environmental variable dependencies.
    """
    @classmethod
    def setUpClass(cls):
        env_vars = {
            'DEBUG': 'true',
            'AWS_DEFAULT_REGION': 'us-west-1',
            'APP_NAME': 'launcher',
            'SUB_DOMAIN': 'foo.bar',
            'DYNAMODB_SERVERS_TABLE_NAME': 'servers-table',
            'LAUNCHER_FUNCTION_ARN': 'arn:aws:stuff:like:an/arn'
        }
        os.environ.update(env_vars)
        cls.build_resources()
        cls.addClassCleanup(cls.destroy_resources)

    @classmethod
    def build_resources(cls):
        import boto3

        dynamodb = boto3.resource('dynamodb')
        cls.table = dynamodb.create_table(
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

    @classmethod
    def destroy_resources(cls):
        cls.table.delete()
