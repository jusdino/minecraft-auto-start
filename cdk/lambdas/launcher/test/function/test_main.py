import os

from moto import mock_aws
from test import LauncherTst


@mock_aws
class TestMain(LauncherTst):
    def test_main(self):
        """
        Ensure a full run from the entrypoint succeeds, then check some details of the architecture
        provisioned and make sure that a second run of the same entrypoint is harmless
        """
        import boto3
        from main import main

        ec2 = boto3.resource('ec2')
        route53 = boto3.client('route53')
        record_sets = tuple(
            r for r in
            route53.list_resource_record_sets(
                HostedZoneId=os.environ['HOSTED_ZONE_ID']
            )['ResourceRecordSets']
            if r['Type'] == 'A'
        )

        # Number of DNS records added
        self.assertEqual(0, len(record_sets))
        # Number of running ec2 instances
        instances = tuple(x for x in ec2.instances.filter(
            Filters=[
                {
                    'Name': 'instance-state-name',
                    'Values': ['running']
                }
            ]
        ).all())
        self.assertEqual(0, len(instances))

        event = {
            'server_name': 'foo',
            'instance_configuration': {
                'instance_type': 't3.xlarge',
                'volume_size': 50,
                'memory_size': '10240m',
                'java_version': '17'
            }
        }
        main(event, {})

        record_sets = tuple(
            r for r in
            route53.list_resource_record_sets(
                HostedZoneId=os.environ['HOSTED_ZONE_ID']
            )['ResourceRecordSets']
            if r['Type'] == 'A'
        )
        # Should have one instance running, one DNS record added
        self.assertEqual(1, len(record_sets))
        instances = tuple(x for x in ec2.instances.filter(
            Filters=[
                {
                    'Name': 'instance-state-name',
                    'Values': ['running']
                }
            ]
        ).all())
        self.assertEqual(1, len(instances))
        # Make sure the instance ip actually corresponds to the new DNS record value
        elastic_ip_address = record_sets[0]['ResourceRecords'][0]['Value']
        self.assertEqual(elastic_ip_address, instances[0].public_ip_address)

        # Running a second time shouldn't change anything, since the instance is already running
        main(event, {})

        record_sets = tuple(
            r for r in
            route53.list_resource_record_sets(
                HostedZoneId=os.environ['HOSTED_ZONE_ID']
            )['ResourceRecordSets']
            if r['Type'] == 'A'
        )
        self.assertEqual(1, len(record_sets))
        self.assertEqual(1, len(tuple(r for r in record_sets if r['Type'] == 'A')))
        self.assertEqual(1, len(tuple(x for x in ec2.instances.all())))
        expected = event['instance_configuration']
        instance = instances[0]
        self.assertEqual(expected['instance_type'], instance.instance_type)
        addresses = ec2.meta.client.describe_addresses()['Addresses']
        # Make sure we've gracefully reused the 'orphaned' elastic ip address
        self.assertEqual(1, len(addresses))
        self.assertEqual(elastic_ip_address, instances[0].public_ip_address)
        ec2.instances.all().terminate()

    def test_main_reuse(self):
        """
        Test that a second run gracefully reuses an 'orphaned' ip address
        """
        import boto3
        from main import main

        ec2 = boto3.resource('ec2')
        route53 = boto3.client('route53')
        event = {
            'server_name': 'foo',
            'instance_configuration': {
                'instance_type': 't3.xlarge',
                'volume_size': 50,
                'memory_size': '10240m',
                'java_version': '17'
            }
        }
        main(event, {})

        instances = tuple(x for x in ec2.instances.filter(
            Filters=[
                {
                    'Name': 'instance-state-name',
                    'Values': ['running']
                }
            ]
        ).all())
        # Sanity checks that something hasn't gone weird in our test
        self.assertEqual(1, len(instances))
        orphaned_address = instances[0].public_ip_address
        instances[0].terminate()

        addresses = ec2.meta.client.describe_addresses()['Addresses']
        self.assertEqual(1, len(addresses))
        # These don't get cleaned up right away by ec2
        for address in addresses:
            ec2.meta.client.disassociate_address(
                AssociationId=address['AssociationId']
            )

        # Because the ec2 instance is expected to clean up its own ip address and we haven't done
        # that explicitly here, there is now an orphaned elastic ip address
        main(event, {})

        record_sets = tuple(
            r for r in
            route53.list_resource_record_sets(
                HostedZoneId=os.environ['HOSTED_ZONE_ID']
            )['ResourceRecordSets']
            if r['Type'] == 'A'
        )
        self.assertEqual(1, len(record_sets))
        self.assertEqual(1, len(tuple(r for r in record_sets if r['Type'] == 'A')))
        self.assertEqual(1, len(tuple(x for x in ec2.instances.filter(
            Filters=[
                {
                    'Name': 'instance-state-name',
                    'Values': ['running']
                }
            ]
        ).all())))
        expected = event['instance_configuration']
        instances = tuple(x for x in ec2.instances.filter(
            Filters=[
                {
                    'Name': 'instance-state-name',
                    'Values': ['running']
                }
            ]
        ).all())
        # Make sure we only have 1 running instance
        self.assertEqual(1, len(instances))
        instance = instances[0]
        self.assertEqual(expected['instance_type'], instance.instance_type)
        addresses = ec2.meta.client.describe_addresses()['Addresses']
        # Make sure we've gracefully reused the 'orphaned' elastic ip address
        self.assertEqual(1, len(addresses))
        self.assertEqual(orphaned_address, instances[0].public_ip_address)
