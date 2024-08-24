import json
from unittest.mock import patch
from test import BaseTestMAS


class TestBasicServer(BaseTestMAS):
    def test_basics(self):
        from models import BasicServer

        server = BasicServer(name='name', hostname='host.name')
        self.assertEqual('name', server.name)
        self.assertEqual('host.name', server.hostname)

    def test_default_hostname(self):
        from models import BasicServer, config

        server = BasicServer(name='name')
        self.assertEqual(f'name.{config.sub_domain}', server.hostname)

    def test_get_server_by_hostname(self):
        self.table.put_item(Item={
                'hostname': 'foo.bar',
                'name': 'foo'
            }
        )

        from models import BasicServer

        server = BasicServer.get_server_by_hostname(hostname='foo.bar')
        self.assertEqual('foo.bar', server.hostname)
        self.assertEqual('foo', server.name)
        self.table.delete_item(
            Key={'hostname': 'foo.bar'}
        )


class TestLaunchableServer(BaseTestMAS):
    @patch('models.lambda_', autospec=True)
    def test_launch(self, mock_lambda):
        from models import LaunchableServer

        self.table.put_item(Item={
            'hostname': 'test.foo.bar',
            'name': 'test'
        })
        server = LaunchableServer(name='test')
        server.launch()

        mock_lambda.invoke.assert_called_once()
        kwargs = mock_lambda.invoke.call_args.kwargs
        payload = json.loads(kwargs['Payload'])
        self.assertEqual('test', payload['server_name'])

        item = self.table.get_item(Key={'hostname': 'test.foo.bar'})['Item']
        self.assertEqual(item['version'], 2)

        self.table.delete_item(Key={'hostname': 'test.foo.bar'})

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
            'hostname': 'test.foo.bar',
            'name': 'test',
            'instance_configuration': instance_configuration
        })
        server = LaunchableServer(name='test')
        server.launch()

        mock_lambda.invoke.assert_called_once()
        kwargs = mock_lambda.invoke.call_args.kwargs
        payload = json.loads(kwargs['Payload'])
        self.assertEqual('test', payload['server_name'])
        self.assertEqual(instance_configuration, payload['instance_configuration'])

        item = self.table.get_item(Key={'hostname': 'test.foo.bar'})['Item']
        self.assertEqual(item['version'], 2)

        self.table.delete_item(Key={'hostname': 'test.foo.bar'})
