import os
from datetime import timedelta
from test import BaseTestMAS


class TestConfig(BaseTestMAS):
    def test_os_env(self):
        """
        Test that our config object has our expected
        values pulled from the environment. This really tests
        our BaseTestMAS class as much as anything
        """
        from config import Config

        config = Config()

        self.assertEqual(os.environ['APP_NAME'], config.app_name)
        self.assertEqual('foo.bar', config.sub_domain)
        self.assertEqual('servers-table', config.dynamodb_servers_table_name)
        self.assertIsInstance(config.server_status_ttl, timedelta)
        self.assertIsInstance(config.launcher_timeout, timedelta)
