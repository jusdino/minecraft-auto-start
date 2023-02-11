import os
from unittest import TestCase, main
from unittest.mock import patch


# Just mock these globally once and for all
mock_resource = patch('boto3.resource').__enter__()
mock_client = patch('boto3.client').__enter__()


class BaseTestMAS(TestCase):
    """
    Mock out required env vars then import config so our unit tests
    don't have any particular environmental variable dependencies.
    """
    def setUp(self):
        self.env_vars = {
                'APP_NAME': 'launcher',
                'SUB_DOMAIN': 'foo.bar',
                'DYNAMODB_SERVERS_TABLE_NAME': 'some-table',
                'LAUNCHER_FUNCTION_ARN': 'arn:aws:stuff:like:an/arn'
        }
        with patch.dict(os.environ, self.env_vars):
            from config import config
        
        mock_resource.reset_mock(side_effect=True, return_value=True)
        mock_client.reset_mock(side_effect=True, return_value=True)
