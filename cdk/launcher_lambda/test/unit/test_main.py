from unittest.mock import patch
from marshmallow import ValidationError

from test import LauncherTst


@patch('main.Server', autospec=True)
class TestMain(LauncherTst):
    def test_instance_config(self, mock_server):
        from main import main

        event = {
            'server_name': 'foo.some.org',
            'instance_configuration': {
                'instance_type': 't3.large',
                'volume_size': 20,
                'memory_size': '6144m',
                'java_version': '17'
            }
        }
        main(event, {})

    def test_no_instance_config(self, mock_server):
        from main import main

        event = {
            'server_name': 'foo.some.org'
        }
        with self.assertRaises(ValidationError):
            main(event, {})

    def test_empty_instance_config(self, mock_server):
        from main import main

        event = {
            'server_name': 'foo.some.org',
            'instance_configuration': {}
        }
        with self.assertRaises(ValidationError):
            main(event, {})

    def test_invalid(self, mock_server):
        from main import main

        event = {
            'server_name': 'foo.some.org',
            'instance_configuration': {
                'instance_type': 't3.wut'
            }
        }
        with self.assertRaises(ValidationError):
            main(event, {})
