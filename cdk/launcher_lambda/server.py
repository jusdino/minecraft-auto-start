from typing import List
from logging import Logger
import boto3

from config import Config


ec2 = boto3.resource('ec2')
ec2_client = boto3.client('ec2')
route53 = boto3.client('route53')
ssm = boto3.client('ssm')


class Server():
    """
    A minecraft server on EC2
    """
    def __init__(self, *, config: Config, logger: Logger, server_name: str):
        super().__init__()
        self.server_name = server_name
        self.config = config
        self.logger = logger

    def launch(
            self,
            instance_type: str,
            volume_size: int,
            memory_size: str,
            ):
        if self.already_live():
            self.logger.info('%s is already live - skipping launch', self.server_name)
            return
        self.logger.info('Launching %s', self.server_name)
        self._provision_instance(
            instance_type=instance_type,
            volume_size=volume_size,
            memory_size=memory_size
        )

    def already_live(self, live_states: List[str] = None) -> bool:
        """
        Query EC2 for instances that match this server's name and with a 'live' state
        """
        # Default: Anything except for 'terminated'
        live_states = live_states or \
            [
                'pending',
                'running',
                'shutting-down',
                'stopping',
                'stopped'
            ]
        instances = tuple(x for x in ec2.instances.filter(
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': [
                        self.server_name,
                    ]
                },
                {
                    'Name': 'tag:Environment',
                    'Values': [
                        self.config.environment_name,
                    ]
                },
                {
                    'Name': 'instance-state-name',
                    'Values': live_states
                }
            ]
        ).limit(1).all())
        return bool(instances)

    def _render_user_data(self, memory_size: str):
        with open('resources/user_data.sh', 'r') as f:
            user_data = f.read()
        for k, v in {
            '__SERVER_NAME__': self.server_name,
            '__DATA_BUCKET_ID__': self.config.data_bucket_id,
            '__SUB_DOMAIN__': self.config.sub_domain,
            '__HOSTED_ZONE_ID__': self.config.hosted_zone_id,
            '__AWS_REGION__': self.config.aws_region,
            '__MEMORY__': memory_size
        }.items():
            user_data = user_data.replace(str(k), str(v))
        self.logger.debug('Final rendered user data: \n--------\n%s\n--------\n', user_data)
        return user_data

    def _get_image_id(self):
        """
        AWS provides latest ami ids in ssm parameters for our convenience
        """
        return ssm.get_parameter(
            Name='/aws/service/ami-amazon-linux-latest/amzn2-ami-minimal-hvm-x86_64-ebs'
        )['Parameter']['Value']

    def _provision_instance(
            self,
            instance_type: str,
            volume_size: int,
            memory_size: str,
            ):
        image_id = self._get_image_id()
        tags = self.config.tags.copy()
        tags.append({
            'Key': 'Name',
            'Value': self.server_name
        })
        instance = ec2.create_instances(
            BlockDeviceMappings=[
                {
                    'DeviceName': '/dev/sdb',
                    'Ebs': {
                        # Minimum 125 GB volume size for sc1/st1
                        'VolumeSize': volume_size,
                        'VolumeType': 'gp3',
                        'DeleteOnTermination': True,
                        # 'Throughput': 500
                    }
                }
            ],
            ImageId=image_id,
            InstanceType=instance_type,
            KeyName=self.config.key_name,
            MinCount=1,
            MaxCount=1,
            SecurityGroupIds=[
                self.config.security_group_id
            ],
            SubnetId=self.config.subnet_id,
            IamInstanceProfile={
                'Arn': self.config.instance_profile_arn
            },
            UserData=self._render_user_data(memory_size=memory_size),
            InstanceInitiatedShutdownBehavior='terminate',
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': tags
                },
                {
                    'ResourceType': 'volume',
                    'Tags': tags
                }
            ]
        )[0]
        elastic_ip_data = ec2_client.allocate_address(
            Domain='vpc',
            TagSpecifications=[
                {
                    'ResourceType': 'elastic-ip',
                    'Tags': tags
                },
            ]
        )
        # We can't associate the ip address until the instance is running
        # So we'll wait till it is running
        ec2_client.get_waiter('instance_running').wait(
            Filters=[
                {
                    'Name': 'instance-state-name',
                    'Values': ['running']
                }
            ],
            InstanceIds=[instance.instance_id]
        )
        ec2_client.associate_address(
            AllocationId=elastic_ip_data['AllocationId'],
            InstanceId=instance.instance_id,
        )
        change_set = {
            'Comment': 'Assign to launched server',
            'Changes': [
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': f'{self.server_name}.{self.config.sub_domain}',
                        'Type': 'A',
                        'TTL': 60,
                        'ResourceRecords': [
                            {
                                'Value': elastic_ip_data['PublicIp']
                            }
                        ]
                    }
                }
            ]
        }
        route53.change_resource_record_sets(
            HostedZoneId=self.config.hosted_zone_id,
            ChangeBatch=change_set
        )
