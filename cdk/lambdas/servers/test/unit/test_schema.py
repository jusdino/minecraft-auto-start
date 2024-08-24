from decimal import Decimal
from test import BaseTestMAS


class TestInstanceConfigSchema(BaseTestMAS):
    def test_load_defaults(self):
        from schema import InstanceConfigSchema

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
        from schema import InstanceConfigSchema

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
        from schema import InstanceConfigSchema

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
        from schema import InstanceConfigSchema

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
