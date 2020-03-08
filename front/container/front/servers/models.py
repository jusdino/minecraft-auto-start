import json
import os
from datetime import datetime

from boto3.dynamodb.conditions import Attr
from flask import current_app
from mcstatus import MinecraftServer

from front import dynamodb, ecs


class LaunchableServer():
    table = dynamodb.Table(os.environ['DYNAMODB_SERVERS_TABLE_NAME'])

    @classmethod
    def get_server_by_hostname(cls, hostname):
        from .schema import LaunchableServerSchema

        schema = LaunchableServerSchema()
        item = cls.table.get_item(Key={'hostname': hostname},
                                  ConsistentRead=False,
                                  ReturnConsumedCapacity='NONE')
        current_app.logger.debug('DynamoDB Item: %s', item)
        try:
            return schema.load(item['Item'])
        except KeyError:
            return None

    @classmethod
    def get_all_servers(cls):
        from .schema import LaunchableServerSchema

        schema = LaunchableServerSchema()
        res = cls.table.scan(
            ReturnConsumedCapacity='NONE',
            ConsistentRead=False
        )
        # current_app.logger.debug('DynamoDB Scan: %s', res)
        return [schema.load(server) for server in res['Items']]

    def __init__(self, **kwargs):
        self.data = dict(**kwargs)
        if not self.data.get('hostname', False):
            self.data['hostname'] = f"{self.data['name']}.{current_app.config['SERVER_DOMAIN']}"
        self.status

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
        status = self.data.get('status')
        if status is None or self.status_expired:
            self.update_status()
        return status

    @status.setter
    def status(self, value: dict):
        self.data['status'] = value

    @property
    def status_time(self):
        if self.data.get('status_time') is None:
            self.update_status()
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
            current_app.logger.debug('Setting launch time to None')
            self.data['launch_time'] = None
            return
        current_app.logger.debug('Setting launch time to %s', value)
        self.data['launch_time'] = str(value.timestamp())

    @property
    def launching(self) -> bool:
        if self.launch_time is None:
            return False
        return self.launch_time + current_app.config['LAUNCHER_TIMEOUT'] > datetime.utcnow()

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
        from .schema import ServerStatusSchema

        current_app.logger.info('Updating MCServer %s', str(self))

        if not hasattr(self, '_server'):
            self._server = MinecraftServer.lookup(self.hostname)
        schema = ServerStatusSchema()
        try:
            status = schema.dump(self._server.status())
            # current_app.logger.debug('Setting status to: %s', status)
            self.status = status
        except (ConnectionRefusedError, BrokenPipeError, OSError) as e:
            self.status = schema.dump({})
        if self.data['status']['description']['text'] != 'Offline':
            self.launch_time = None
        self.status_time = datetime.utcnow()

    @property
    def status_expired(self):
        return self.status_time + current_app.config['SERVER_STATUS_TTL'] < datetime.utcnow()

    def save(self):
        from .schema import LaunchableServerSchema

        schema = LaunchableServerSchema()
        version = self.version
        self.version = version + 1
        data = schema.dump(self.data)
        if version > 0:
            # Optimistic lock via condition - let fail if concurrent updates
            self.table.put_item(Item=data, ConditionExpression=Attr('version').eq(version))
        else:
            self.table.put_item(Item=data)

    def launch(self):
        current_app.logger.info('Running task: %s on cluster %s', current_app.config['LAUNCHER_TASK_ARN'], current_app.config['CLUSTER_ARN'])
        ecs.run_task(
            launchType='FARGATE',
            networkConfiguration=current_app.config['LAUNCHER_NETWORK_CONFIG'],
            overrides={
                'containerOverrides': [{
                    'name': 'launcher',
                    'environment': [{
                        'name': 'SERVER_NAME',
                        'value': self.name
                    }]
                }]
            },
            taskDefinition=current_app.config['LAUNCHER_TASK_ARN'],
            cluster=current_app.config['CLUSTER_ARN']
        )
        self.launch_time = datetime.utcnow()
        self.save()

    def __repr__(self):
        return f'<LaunchableServer(name={self.name}, hostname={self.hostname}>'
