import json
import os
import uuid
from unittest import TestCase

import boto3
from moto import mock_aws


route53 = boto3.client('route53')


@mock_aws
class LauncherTst(TestCase):
    """
    Base class for setup common across all test cases
    """
    def setUp(self):
        lambda_env = {
            'DEBUG': 'true',
            'ENV': 'test-env',
            'AWS_DEFAULT_REGION': 'us-west-1',
            'TAGS': json.dumps([{
                'Key': 'Environment',
                'Value': 'test-env'}]),
            'SSH_KEY_NAME': 'foo-key-name',
            'SUB_DOMAIN': 'some.org',
            'DATA_BUCKET_ID': 'some-data-bucket',
            # Will replace with identifiers from moto
            'HOSTED_ZONE_ID': 'foo-id',
            'SECURITY_GROUP_ID': 'sg-00000000000000000',
            'SUBNET_ID': 'subnet-00000000',
            'INSTANCE_PROFILE_ARN': 'arn:aws:iam::000000000000:instance-profile/foo-profile'
        }
        os.environ.update(lambda_env)
        self.build_resources()

    def build_resources(self):
        # Grab mock indentifiers from moto
        ec2 = boto3.resource('ec2')
        security_group = tuple(ec2.security_groups.limit(1).all())[0]
        subnet = tuple(ec2.subnets.limit(1).all())[0]
        os.environ['SECURITY_GROUP_ID'] = security_group.group_id
        os.environ['SUBNET_ID'] = subnet.subnet_id

        iam = boto3.resource('iam')
        self.instance_profile = iam.create_instance_profile(
            InstanceProfileName='foo-profile'
        )
        os.environ['INSTANCE_PROFILE_ARN'] = self.instance_profile.arn
        os.environ['INSTANCE_PROFILE_NAME'] = self.instance_profile.instance_profile_name

        resp = route53.create_hosted_zone(Name='some.org', CallerReference=uuid.uuid4().hex)
        os.environ['HOSTED_ZONE_ID'] = resp['HostedZone']['Id']

    def tearDown(self) -> None:
        super().tearDown()
        self.destroy_resources()

    def destroy_resources(self):
        # Terminate instances
        ec2 = boto3.resource('ec2')
        for instance in ec2.instances.all():
            print(f'Terminating instance {instance.instance_id}')
            instance.terminate()

        # Clean up ip addresses
        addresses = ec2.meta.client.describe_addresses().get('Addresses', [])
        for address in addresses:
            ec2.meta.client.release_address(
                AllocationId=address['AllocationId']
            )
        self.instance_profile.delete()

        # Clean up route53 records
        record_sets = route53.list_resource_record_sets(
            HostedZoneId=os.environ['HOSTED_ZONE_ID']
        )['ResourceRecordSets']
        changes = [
            {
                'Action': 'DELETE',
                'ResourceRecordSet': {
                    'Name': r['Name'],
                    'Type': r['Type'],
                    'TTL': r['TTL'],
                    'ResourceRecords': r['ResourceRecords']
                }
            }
            for r in record_sets
            if r['Type'] == 'A'
        ]
        if changes:
            change_set = {
                'Changes': changes
            }
            route53.change_resource_record_sets(
                HostedZoneId=os.environ['HOSTED_ZONE_ID'],
                ChangeBatch=change_set
            )
        route53.delete_hosted_zone(Id=os.environ['HOSTED_ZONE_ID'])
