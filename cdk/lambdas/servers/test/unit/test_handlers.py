import json
from datetime import datetime, UTC
from decimal import Decimal
from unittest.mock import patch
from moto import mock_aws

from test import BaseTestMAS


@mock_aws
class TestGetServers(BaseTestMAS):
    @patch('models.JavaServer', autospec=True)
    def test_happy(self, mock_java_server):
        with open('test/resources/server_in_dynamo.json', 'r') as f:
            self.table.put_item(Item=json.load(f))

        # Just preempting actual network calls
        mock_java_server.lookup.return_value.status.side_effect = ConnectionRefusedError('connection refused')

        with open('test/resources/apigateway_event.json', 'r') as f:
            event = json.load(f)

        from handlers import get_servers

        resp = get_servers(event, self.mock_context)

        self.assertEqual(200, resp['statusCode'])
        body = json.loads(resp['body'])
        self.assertEqual(
            [{
                'description': 'Just passing through...',
                'favicon': None,
                'hostname': 'test.example.org',
                'mc_version': {'name': 'Paper 1.20.4', 'protocol': 765},
                'name': 'test',
                'players': {'max': 0, 'online': 0},
                'status_time': 10.0,
                'version': 227
            }],
            body
        )


@mock_aws
class TestGetOneServer(BaseTestMAS):
    @patch('models.JavaServer', autospec=True)
    def test_happy(self, mock_java_server):
        with open('test/resources/server_in_dynamo.json', 'r') as f:
            self.table.put_item(Item=json.load(f))

        # Just pre-empting actual network calls
        mock_java_server.lookup.return_value.status.side_effect = ConnectionRefusedError('connection refused')

        with open('test/resources/apigateway_event.json', 'r') as f:
            event = json.load(f)
        event['pathParameters'] = {
            'hostname': 'test.example.org'
        }

        from handlers import get_one_server

        resp = get_one_server(event, self.mock_context)

        self.assertEqual(200, resp['statusCode'])
        body = json.loads(resp['body'])

        # Status time will be updated to a dynamic value, so we'll pop it and just check its type
        status_time = body.pop('status_time')
        self.assertIsInstance(status_time, float)

        self.assertEqual(
            {
                'description': 'Just passing through...',
                'favicon': None,
                'hostname': 'test.example.org',
                'launch_time': 10.0,
                'instance_configuration': {
                    'instance_type': 't3.large',
                    'java_version': '17',
                    'memory_size': '6144m',
                    's3_schematic_prefix': 'common',
                    'volume_size': 20
                },
                'mc_version': {'name': 'Paper 1.20.4', 'protocol': 765},
                'name': 'test',
                'online': False,
                'launching': False,
                'players': {'max': 0, 'online': 0},
                'version': 228
            },
            body
        )

    @patch('models.JavaServer', autospec=True)
    def test_online_false(self, mock_java_server):
        self.table.put_item(Item={
            "hostname": "test.example.org",
            "description": "Offline",
            "favicon": None,
            "instance_configuration": {
                "instance_type": "t3.large",
                "java_version": "17",
                "memory_size": "6144m",
                "s3_schematic_prefix": "common",
                "volume_size": 20
            },
            "launch_time": 1733728419,
            "mc_version": {
                "name": "N/A",
                "protocol": -1
            },
            "name": "test",
            "players": {
                "max": 0,
                "online": 0
            },
            "online": False,
            # Make sure status_time is fresh, so we don't update status
            "status_time": Decimal(datetime.now(tz=UTC).timestamp()),
            "version": 228
        })

        # Just pre-empting actual network calls
        mock_java_server.lookup.return_value.status.side_effect = ConnectionRefusedError('connection refused')

        with open('test/resources/apigateway_event.json', 'r') as f:
            event = json.load(f)
        event['pathParameters'] = {
            'hostname': 'test.example.org'
        }

        from handlers import get_one_server

        resp = get_one_server(event, self.mock_context)

        self.assertEqual(200, resp['statusCode'])
        body = json.loads(resp['body'])

        # Status time will be updated to a dynamic value, so we'll pop it and just check its type
        status_time = body.pop('status_time')
        self.assertIsInstance(status_time, float)

        self.assertEqual(
            {
                'description': 'Offline',
                'favicon': None,
                'hostname': 'test.example.org',
                'launch_time': 1733728419,
                'instance_configuration': {
                    'instance_type': 't3.large',
                    'java_version': '17',
                    'memory_size': '6144m',
                    's3_schematic_prefix': 'common',
                    'volume_size': 20
                },
                'mc_version': {'name': 'N/A', 'protocol': -1},
                'name': 'test',
                'online': False,
                'launching': False,
                'players': {'max': 0, 'online': 0},
                'version': 228
            },
            body
        )
        mock_java_server.lookup.return_value.status.assert_not_called()


@mock_aws
class TestLaunchServer(BaseTestMAS):
    @patch('models.lambda_', autospec=True)
    @patch('models.JavaServer', autospec=True)
    def test_happy(self, mock_java_server, mock_lambda):
        with open('test/resources/server_in_dynamo.json', 'r') as f:
            self.table.put_item(Item=json.load(f))

        # Just pre-empting actual network calls
        mock_java_server.lookup.return_value.status.side_effect = ConnectionRefusedError('connection refused')

        with open('test/resources/apigateway_event.json', 'r') as f:
            event = json.load(f)
        event['pathParameters'] = {
            'hostname': 'test.example.org'
        }

        from handlers import launch_server

        resp = launch_server(event, self.mock_context)

        self.assertEqual(200, resp['statusCode'])
        body = json.loads(resp['body'])
        self.assertEqual('test.example.org', body['hostname'])
        mock_lambda.invoke.assert_called_once()
