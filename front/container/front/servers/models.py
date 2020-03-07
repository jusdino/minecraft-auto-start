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
        item = cls.table.get_item(Key={'hostname': hostname},
                                  ConsistentRead=False,
                                  ReturnConsumedCapacity='NONE')
        current_app.logger.debug('DynamoDB Item: %s', item)
        try:
            return cls(**item['Item'])
        except KeyError:
            return None

    @classmethod
    def get_all_servers(cls):
        res = cls.table.scan(
            ReturnConsumedCapacity='NONE',
            ConsistentRead=False
        )
        # current_app.logger.debug('DynamoDB Scan: %s', res)
        return [cls(**server) for server in res['Items']]

    def __init__(self, **kwargs):
        self._data = dict(**kwargs)
        if not self._data.get('hostname', False):
            self._data['hostname'] = f"{self._data['name']}.{current_app.config['SERVER_DOMAIN']}"

    @property
    def name(self):
        return self._data['name']

    @name.setter
    def name(self, value):
        self._data['name'] = value

    @property
    def hostname(self):
        return self._data['hostname']

    @hostname.setter
    def hostname(self, value):
        self._data['hostname'] = value

    @property
    def _status(self):
        return self._data['_status']

    @_status.setter
    def _status(self, value):
        self._data['_status'] = value

    @property
    def status_time(self):
        return datetime.fromtimestamp(float(self._data['status_time']))

    @status_time.setter
    def status_time(self, value: datetime):
        self._data['status_time'] = str(value.timestamp())

    @property
    def status(self):
        from .schema import ServerStatusSchema

        schema = ServerStatusSchema()
        try:
            status = self._status
        except KeyError:
            status = None
        if status is None or self.status_expired:
            self.update_status()
        return schema.loads(self._status)

    @status.setter
    def status(self, new_status):
        from .schema import ServerStatusSchema

        schema = ServerStatusSchema()
        self._status = schema.dumps(new_status)

    def update_status(self):
        from .schema import ServerStatusSchema

        current_app.logger.info('Updating MCServer %s', str(self))

        if not hasattr(self, '_server'):
            self._server = MinecraftServer.lookup(self.hostname)
        schema = ServerStatusSchema()
        try:
            status = self._server.status()
            self._status = schema.dumps(status)
        except (ConnectionRefusedError, BrokenPipeError, OSError):
            self._status = schema.dumps({})
        self.status_time = datetime.utcnow()
        return self._status

    @property
    def status_expired(self):
        return self.status_time + current_app.config['SERVER_STATUS_TTL'] < datetime.utcnow()

    def save(self):
        version = self._data.get('version', 0)
        self._data['version'] = version + 1
        if version > 0:
            # Optimistic lock via condition - let fail if concurrent updates
            self.table.put_item(Item=self._data, ConditionExpression=Attr('version').eq(version))
        else:
            self.table.put_item(Item=self._data)

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

    def __repr__(self):
        return f'<LaunchableServer(name={self.name}, hostname={self.hostname}>'
