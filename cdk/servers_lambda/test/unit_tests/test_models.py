from test import BaseTestMAS, mock_resource


class TestBasicServer(BaseTestMAS):
    def test_basics(self):
        from models import BasicServer

        server = BasicServer(name='name', hostname='host.name')
        self.assertEqual('name', server.name)
        self.assertEqual('host.name', server.hostname)

    def test_default_hostname(self):
        from models import BasicServer
        from config import config

        server = BasicServer(name='name')
        self.assertEqual(f'name.{config["SERVER_DOMAIN"]}', server.hostname)

    def test_get_server_by_hostname(self):
        mock_table = mock_resource.return_value.Table.return_value
        mock_table.get_item.return_value = {
            'Item': {
                'hostname': 'foo.bar',
                'name': 'foo'
            }
        }

        from models import BasicServer

        server = BasicServer.get_server_by_hostname(hostname='foo.bar')
        self.assertEqual('foo.bar', server.hostname)
        self.assertEqual('foo', server.name)
