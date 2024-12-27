from datetime import UTC, datetime
from decimal import Decimal
from test import BaseTestMAS


class TestLaunchableServerSchema(BaseTestMAS):
    def test_can_load_legacy_record(self):
        from schema.launchable_server import LaunchableServerSchema

        schema = LaunchableServerSchema()
        print('Hooks: ', schema._hooks)
        record = {
            'hostname': 'test.example.org',
            'instance_configuration': {
                'instance_type': 't3.large',
                'java_version': '22',
                'memory_size': '6144m',
                's3_schematic_prefix': 'common',
                'volume_size': 20
            },
            'launch_time': None,
            'name': 'test',
            'status': '{"description": {"text": "Some helpful description"}, "players": {"max": 0, "online": 0}, "version": {"name": "N/A", "protocol": "N/A"}, "favicon": "somebase64imagedata"}',
            'status_time': '1735012099.828149',
            'version': 5449
        }
        loaded = schema.load(record)

        # Launch time's default value will be dynamic, so we'll pop it and just
        # check its type.
        launch_time = loaded.pop('launch_time')
        self.assertIsInstance(launch_time, datetime)

        self.assertEqual(
            {
                'name': 'test',
                'hostname': 'test.example.org',
                'description': 'Some helpful description',
                'mc_version': {'name': 'N/A', 'protocol': -1},
                'favicon': "somebase64imagedata",
                'instance_configuration': {
                    'instance_type': 't3.large',
                    'java_version': '22',
                    'memory_size': '6144m',
                    's3_schematic_prefix': 'common',
                    'volume_size': 20
                },
                'status_time': datetime(2024, 12, 24, 3, 48, 19, 828149, tzinfo=UTC),
                'online': False,
                'players': {'max': 0, 'online': 0},
                'version': 5449
            },
            loaded
        )

    def test_dump_decimal_times(self):
        from schema.launchable_server import LaunchableServerSchema

        schema = LaunchableServerSchema()
        raw = {
            'name': 'foo',
            'hostname': 'foo.example.org',
        }
        loaded = schema.load(raw)
        self.assertIsInstance(loaded['status_time'], datetime)
        self.assertIsInstance(loaded['launch_time'], datetime)

        dumped = schema.dump(loaded)
        self.assertIsInstance(dumped['status_time'], Decimal)
        self.assertIsInstance(dumped['launch_time'], Decimal)

    def test_load_defaults(self):
        from schema.launchable_server import LaunchableServerSchema

        schema = LaunchableServerSchema()

        loaded = schema.load({
            'hostname': 'test.example.org',
            'name': 'test'
        })

        # time defaults are dynamic so we'll pop them and just check their types
        launch_time = loaded.pop('launch_time')
        status_time = loaded.pop('status_time')
        self.assertIsInstance(launch_time, datetime)
        self.assertIsInstance(status_time, datetime)

        self.assertEqual(
            {
                'hostname': 'test.example.org',
                'name': 'test',
                'description': 'A Minecraft server',
                'online': False,
                'mc_version': {'name': 'N/A', 'protocol': -1},
                'favicon': None,
                'instance_configuration': {
                    'instance_type': 't3.large',
                    'java_version': '17',
                    'memory_size': '6144m',
                    's3_schematic_prefix': 'common',
                    'volume_size': 20
                },
                'players': {'max': 0, 'online': 0},
                'version': 0
            },
            loaded
        )


class TestInstanceConfigSchema(BaseTestMAS):
    def test_load_defaults(self):
        from schema.instance_config import InstanceConfigSchema

        schema = InstanceConfigSchema()
        loaded = schema.load({})
        self.assertEqual(
            {
                'instance_type': 't3.large',
                'volume_size': 20,
                'memory_size': '6144m',
                'java_version': '17',
                's3_schematic_prefix': 'common'
            },
            loaded
        )

    def test_load_values(self):
        from schema.instance_config import InstanceConfigSchema

        schema = InstanceConfigSchema()
        raw = {
            'instance_type': 't3.xlarge',
            'volume_size': 50,
            'memory_size': '10240m',
            'java_version': '8',
            's3_schematic_prefix': 'foo'
        }
        loaded = schema.load(raw)
        self.assertEqual(
            {
                'instance_type': 't3.xlarge',
                'volume_size': 50,
                'memory_size': '10240m',
                'java_version': '8',
                's3_schematic_prefix': 'foo'
            },
            loaded
        )

    def test_load_new_java(self):
        from schema.instance_config import InstanceConfigSchema

        schema = InstanceConfigSchema()
        raw = {
            'instance_type': 't3.xlarge',
            'volume_size': 50,
            'memory_size': '10240m',
            'java_version': '22',
            's3_schematic_prefix': 'foo'
        }
        loaded = schema.load(raw)
        self.assertEqual(
            {
                'instance_type': 't3.xlarge',
                'volume_size': 50,
                'memory_size': '10240m',
                'java_version': '22',
                's3_schematic_prefix': 'foo'
            },
            loaded
        )

    def test_load_decimal(self):
        from schema.instance_config import InstanceConfigSchema

        schema = InstanceConfigSchema()
        raw = {
            'instance_type': 't3.xlarge',
            'volume_size': Decimal(50),
            'memory_size': '10240m',
            'java_version': '8',
            's3_schematic_prefix': 'foo'
        }
        loaded = schema.load(raw)
        self.assertEqual(
            {
                'instance_type': 't3.xlarge',
                'volume_size': 50,
                'memory_size': '10240m',
                'java_version': '8',
                's3_schematic_prefix': 'foo'
            },
            loaded
        )
