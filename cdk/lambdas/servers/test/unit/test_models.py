from datetime import UTC, datetime, timedelta
from decimal import Decimal
import json
from unittest.mock import patch
from marshmallow import ValidationError
from moto import mock_aws
from test import BaseTestMAS


@mock_aws
class TestBasicServer(BaseTestMAS):
    def test_basics(self):
        from models import BasicServer

        server = BasicServer(name='name', hostname='host.name')
        self.assertEqual('name', server.data['name'])
        self.assertEqual('host.name', server.data['hostname'])

    def test_get_server_by_hostname(self):
        self.table.put_item(Item={
                'hostname': 'foo.example.org',
                'name': 'foo'
            }
        )

        from models import BasicServer

        server = BasicServer.get_server_by_hostname(hostname='foo.example.org')
        self.assertEqual('foo.example.org', server.data['hostname'])
        self.assertEqual('foo', server.data['name'])

    @patch('models.JavaServer', autospec=True)
    def test_update_if_expired(self, mock_java_server):
        with open('test/resources/server_in_dynamo.json', 'r') as f:
            self.table.put_item(Item=json.load(f))

        # Just pre-empting actual network calls
        mock_java_server.lookup.return_value.status.side_effect = ConnectionRefusedError('connection refused')

        from models import BasicServer

        server = BasicServer.get_server_by_hostname(hostname='test.example.org')
        server.update_if_expired()

        mock_java_server.lookup.return_value.status.assert_called_once()

    @patch('models.JavaServer', autospec=True)
    def test_not_update_if_not_expired(self, mock_java_server):
        with open('test/resources/server_in_dynamo.json', 'r') as f:
            server = json.load(f)
        # Pretty fresh status
        status_time = datetime.now(tz=UTC) - timedelta(seconds=1)
        server['status_time'] = Decimal(status_time.timestamp())
        self.table.put_item(Item=server)

        # Just pre-empting actual network calls
        mock_java_server.lookup.return_value.status.side_effect = ConnectionRefusedError('connection refused')

        from models import BasicServer

        server = BasicServer.get_server_by_hostname(hostname='test.example.org')
        server.update_if_expired()

        mock_java_server.lookup.return_value.status.assert_not_called()
        self.assertEqual(status_time, server['status_time'])


@mock_aws
class TestLaunchableServer(BaseTestMAS):
    def test_not_launching(self):
        self.table.put_item(Item={
                'hostname': 'foo.example.org',
                'name': 'foo',
                'launch_time': Decimal('1.0')  # One second after the epoch (a long time ago)
            }
        )

        from models import LaunchableServer

        server = LaunchableServer.get_server_by_hostname(hostname='foo.example.org')
        server.update_from_db()
        self.assertFalse(server.launching)

    def test_launching(self):
        from config import config

        self.table.put_item(Item={
                'hostname': 'foo.example.org',
                'name': 'foo',
                'launch_time': Decimal((datetime.now(tz=UTC) - config.launcher_timeout/2).timestamp())  # within the timeout
            }
        )

        from models import LaunchableServer

        server = LaunchableServer.get_server_by_hostname(hostname='foo.example.org')
        server.update_from_db()
        self.assertTrue(server.launching)

    @patch('models.lambda_', autospec=True)
    def test_launch(self, mock_lambda):
        from models import LaunchableServer

        self.table.put_item(Item={
            'hostname': 'test.example.org',
            'name': 'test'
        })
        server = LaunchableServer.get_server_by_hostname(hostname='test.example.org')
        server.launch()

        mock_lambda.invoke.assert_called_once()
        kwargs = mock_lambda.invoke.call_args.kwargs
        payload = json.loads(kwargs['Payload'])
        self.assertEqual('test', payload['server_name'])

        item = self.table.get_item(Key={'hostname': 'test.example.org'})['Item']
        self.assertEqual(item['version'], 1)

    @patch('models.lambda_', autospec=True)
    def test_second_launch(self, mock_lambda):
        from models import LaunchableServer

        self.table.put_item(Item={
            'hostname': 'test.example.org',
            'name': 'test',
            'version': 1
        })
        server = LaunchableServer(name='test', hostname='test.example.org')
        server.update_from_db()
        server.launch()

        mock_lambda.invoke.assert_called_once()
        kwargs = mock_lambda.invoke.call_args.kwargs
        payload = json.loads(kwargs['Payload'])
        self.assertEqual('test', payload['server_name'])

        item = self.table.get_item(Key={'hostname': 'test.example.org'})['Item']
        self.assertEqual(item['version'], 2)

    @patch('models.lambda_', autospec=True)
    def test_concurrent_update(self, mock_lambda):
        from models import LaunchableServer

        self.table.put_item(Item={
            'hostname': 'test.example.org',
            'name': 'test',
            'version': 1
        })
        server = LaunchableServer(name='test', hostname='test.example.org')
        server.update_from_db()
        self.table.put_item(Item={
            'hostname': 'test.example.org',
            'name': 'test',
            'version': 2
        })
        server.launch()

        mock_lambda.invoke.assert_called_once()
        kwargs = mock_lambda.invoke.call_args.kwargs
        payload = json.loads(kwargs['Payload'])
        self.assertEqual('test', payload['server_name'])

        item = self.table.get_item(Key={'hostname': 'test.example.org'})['Item']
        self.assertEqual(item['version'], 3)

    @patch('models.lambda_', autospec=True)
    def test_launch_with_instance_config(self, mock_lambda):
        from models import LaunchableServer

        instance_configuration = {
            'instance_type': 't3.2xlarge',
            'volume_size': 12,
            'memory_size': '1234m',
            'java_version': '8',
            's3_schematic_prefix': 'foo'
        }
        self.table.put_item(Item={
            'hostname': 'test.example.org',
            'name': 'test',
            'instance_configuration': instance_configuration
        })
        server = LaunchableServer(name='test', hostname='test.example.org')
        server.update_from_db()
        server.launch()

        mock_lambda.invoke.assert_called_once()
        kwargs = mock_lambda.invoke.call_args.kwargs
        payload = json.loads(kwargs['Payload'])
        self.assertEqual('test', payload['server_name'])
        self.assertEqual(instance_configuration, payload['instance_configuration'])

        item = self.table.get_item(Key={'hostname': 'test.example.org'})['Item']
        self.assertEqual(item['version'], 1)
