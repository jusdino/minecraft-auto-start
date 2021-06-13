import os
from datetime import datetime

import boto3
from boto3.dynamodb.conditions import Attr
from mcstatus import MinecraftServer

from config import config, logger

dynamodb = boto3.resource('dynamodb')
ecs = boto3.client('ecs')


class LaunchableServer():
    table = dynamodb.Table(config['DYNAMODB_SERVERS_TABLE_NAME'])

    def __init__(self, **kwargs):
        self.data = dict(**kwargs)
        if not self.data.get('hostname', False):
            self.data['hostname'] = f"{self.data['name']}.{config['SERVER_DOMAIN']}"
        if self.status is None or self.status_expired:
            self.update_status()

    @classmethod
    def get_server_by_hostname(cls, hostname, consistent_read=False):

        from schema import LaunchableServerSchema
        schema = LaunchableServerSchema()
        item = cls.table.get_item(Key={'hostname': hostname},
                                  ConsistentRead=consistent_read,
                                  ReturnConsumedCapacity='NONE')
        # logger.debug('DynamoDB Item: %s', item)
        try:
            return cls(**schema.load(item['Item']))
        except KeyError:
            return None

    @classmethod
    def get_all_servers(cls, consistent_read=False):
        from schema import LaunchableServerSchema

        schema = LaunchableServerSchema()
        res = cls.table.scan(
            ReturnConsumedCapacity='NONE',
            ConsistentRead=consistent_read
        )
        # logger.debug('DynamoDB Scan: %s', res)
        return [cls(**schema.load(server)) for server in res['Items']]

    @property
    def name(self):
        return self.data['name']

    @name.setter
    def name(self, value):
        self.data['name'] = value

    @property
    def hostname(self):
        return self.data['hostname']

    @hostname.setter
    def hostname(self, value):
        self.data['hostname'] = value

    @property
    def status(self) -> dict:
        return self.data.get('status')

    @status.setter
    def status(self, value: dict):
        self.data['status'] = value

    @property
    def status_time(self):
        if self.data.get('status_time') is None:
            return None
        return datetime.fromtimestamp(float(self.data['status_time']))

    @status_time.setter
    def status_time(self, value: datetime):
        self.data['status_time'] = str(value.timestamp())

    @property
    def launch_time(self) -> (datetime, None):
        launch_time = self.data.get('launch_time')
        if launch_time is None:
            return None
        return datetime.fromtimestamp(float(launch_time))

    @launch_time.setter
    def launch_time(self, value: datetime):
        if value is None:
            logger.debug('Setting launch time to None')
            self.data['launch_time'] = None
            return
        logger.debug('Setting launch time to %s', value)
        self.data['launch_time'] = str(value.timestamp())

    @property
    def launching(self) -> bool:
        if self.launch_time is None:
            return False
        return self.launch_time + config['LAUNCHER_TIMEOUT'] > datetime.utcnow()

    @property
    def version(self) -> int:
        try:
            return self.data['version']
        except KeyError as e:
            raise AttributeError from e

    @version.setter
    def version(self, value: int):
        self.data['version'] = value

    def update_status(self):
        from schema import ServerStatusSchema, LaunchableServerSchema

        logger.info('Updating MCServer %s', str(self))

        # Grab fresh data with consistent_read to DB
        item = self.table.get_item(Key={'hostname': self.hostname},
                                   ConsistentRead=True,
                                   ReturnConsumedCapacity='NONE')
        # logger.debug('DynamoDB Item: %s', item)
        server_schema = LaunchableServerSchema()
        try:
            self.data = server_schema.load(item['Item'])
        except KeyError:
            return
        if self.status is not None and not self.status_expired:
            return

        if not hasattr(self, '_server'):
            self._server = MinecraftServer.lookup(self.hostname)
        status_schema = ServerStatusSchema()
        try:
            status = status_schema.dump(self._server.status())
            # logger.debug('Setting status to: %s', status)
            self.status = status
        except (ConnectionRefusedError, BrokenPipeError, OSError):
            self.status = status_schema.dump({})
        if self.data['status']['description']['text'] != 'Offline' or not self.launching:
            self.launch_time = None
        self.status_time = datetime.utcnow()
        self.save()

    @property
    def status_expired(self):
        if self.status_time is None:
            return True
        return self.status_time + config['SERVER_STATUS_TTL'] < datetime.utcnow()

    def save(self):
        from schema import LaunchableServerSchema

        schema = LaunchableServerSchema()
        version = self.version
        self.version = version + 1
        data = schema.dump(self.data)
        logger.info('Updating DB for %s', self.hostname)
        if version > 0:
            # Optimistic lock via condition - let fail if concurrent updates
            self.table.put_item(Item=data, ConditionExpression=Attr('version').eq(version))
        else:
            self.table.put_item(Item=data)

    def launch(self):
        logger.info('Running task: %s on cluster %s', config['LAUNCHER_TASK_ARN'], config['CLUSTER_ARN'])
        ecs.run_task(
            launchType='FARGATE',
            networkConfiguration=config['LAUNCHER_NETWORK_CONFIG'],
            overrides={
                'containerOverrides': [{
                    'name': 'launcher',
                    'environment': [{
                        'name': 'SERVER_NAME',
                        'value': self.name
                    }]
                }]
            },
            taskDefinition=config['LAUNCHER_TASK_ARN'],
            cluster=config['CLUSTER_ARN']
        )
        self.launch_time = datetime.utcnow()

    def __repr__(self):
        return f'<LaunchableServer(name={self.name}, hostname={self.hostname}>'
