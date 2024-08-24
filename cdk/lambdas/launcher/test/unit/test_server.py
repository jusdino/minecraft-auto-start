from test import LauncherTst


class TestServer(LauncherTst):
    def setUp(self):
        super().setUp()
        from server import Server

        from main import Config, logger
        self.server = Server(config=Config(), logger=logger, server_name='foo.some.org')

    def test_basics(self):
        self.assertEqual('foo.some.org', self.server.server_name)

    def test_not_already_live(self):
        self.assertFalse(self.server.already_live())

    def test_launch(self):
        self.assertFalse(self.server.already_live())
        self.server.launch(
            instance_type='t3.small',
            volume_size=10,
            memory_size='1024m',
            java_version='8',
            s3_schematic_prefix=None
        )
        self.assertTrue(self.server.already_live())
