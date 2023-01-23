import json
import os

from test import LauncherTst


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
        self.assertEqual(0, len(tuple(x for x in ec2.instances.all())))

        with open('test/resources/sample_lambda_event.json', 'r') as f:
            event = json.load(f)
        main(event, {})

        record_sets = tuple(r for r in
            route53.list_resource_record_sets(
                HostedZoneId=os.environ['HOSTED_ZONE_ID']
            )['ResourceRecordSets']
            if r['Type'] == 'A'
        )
        # Should have one instance running, one DNS record added
        self.assertEqual(1, len(record_sets))
        instances = tuple(x for x in ec2.instances.all())
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
