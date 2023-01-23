import json
import os
import uuid
from unittest import TestCase

import moto


mock_iam = moto.mock_iam()
mock_ec2 = moto.mock_ec2()
mock_ssm = moto.mock_ssm()
mock_route53 = moto.mock_route53()

mock_iam.start()
mock_ec2.start()
mock_ssm.start()
mock_route53.start()


class LauncherTst(TestCase):
    """
    Base class for setup common across all test cases
    """
    @classmethod
    def setUpClass(cls):
        lambda_env = {
            'DEBUG': 'true',
            'AWS_DEFAULT_REGION': 'us-west-1',
            'TAGS': json.dumps([{
                'Key': 'foo',
                'Value': 'bar'}]),
            'SSH_KEY_NAME': 'foo-key-name',
            'HOSTED_ZONE_NAME': 'some.org',
            'DATA_BUCKET_ID': 'some-data-bucket',
            # Will replace with identifiers from moto
            'HOSTED_ZONE_ID': 'foo-id',
            'SECURITY_GROUP_ID': 'sg-00000000000000000',
            'SUBNET_ID': 'subnet-00000000',
            'INSTANCE_PROFILE_ARN': 'arn:aws:iam::000000000000:instance-profile/foo-profile'
        }
        os.environ.update(lambda_env)
        # Grab mock indentifiers from moto
        import boto3
        ec2 = boto3.resource('ec2')
        security_group = tuple(x for x in ec2.security_groups.limit(1).all())[0]
        subnet = tuple(x for x in ec2.subnets.limit(1).all())[0]
        os.environ['SECURITY_GROUP_ID'] = security_group.group_id
        os.environ['SUBNET_ID'] = subnet.subnet_id
        cls.build_resources()
        cls.addClassCleanup(cls.destroy_resources)

    @classmethod
    def build_resources(cls):
        import boto3

        route53 = boto3.client('route53')
        resp = route53.create_hosted_zone(Name='some.org', CallerReference=uuid.uuid4().hex)
        os.environ['HOSTED_ZONE_ID'] = resp['HostedZone']['Id']
        iam = boto3.resource('iam')
        cls.instance_profile = iam.create_instance_profile(
            InstanceProfileName='foo-profile'
        )
        os.environ['INSTANCE_PROFILE_ARN'] = cls.instance_profile.arn
        os.environ['INSTANCE_PROFILE_NAME'] = cls.instance_profile.instance_profile_name

    @classmethod
    def destroy_resources(cls):
        import boto3

        route53 = boto3.client('route53')
        route53.delete_hosted_zone(Id=os.environ['HOSTED_ZONE_ID'])
        cls.instance_profile.delete()

    def tearDown(self) -> None:
        import boto3
        # Terminate instances
        ec2 = boto3.resource('ec2')
        for instance in ec2.instances.all():
            instance.terminate()

        # Clean up route53 records
        route53 = boto3.client('route53')
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

