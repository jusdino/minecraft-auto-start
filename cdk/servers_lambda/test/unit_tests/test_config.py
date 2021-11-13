from test import BaseTestMAS


class TestConfig(BaseTestMAS):
    def test_os_env(self):
        """
        Test that our config object has our expected
        values pulled from the environment. This really tests
        our BaseTestMAS class as much as anything
        """
        from config import config

        for k, v in self.env_vars.items():
            self.assertEqual(v, config[k])
