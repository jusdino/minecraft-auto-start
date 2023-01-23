import json
from datetime import datetime
from random import randint
from time import sleep
import typing

import boto3
from boto3.dynamodb.conditions import Attr
from mcstatus import MinecraftServer

from schema import BasicServerSchema, LaunchableServerSchema
from config import config, logger


dynamodb = boto3.resource('dynamodb')
lambda_ = boto3.client('lambda')


class BasicServer():
    table = dynamodb.Table(config['DYNAMODB_SERVERS_TABLE_NAME'])
    schema = BasicServerSchema

    def __init__(self, **kwargs):
        self.data = dict(**kwargs)
        if not self.data.get('hostname', False):
            self.data['hostname'] = f"{self.data['name']}.{config['SERVER_DOMAIN']}"

    @classmethod
    def get_server_by_hostname(cls, hostname, consistent_read=False):
        logger.info('Fetching record for %s', hostname)
        schema = cls.schema()
        item = cls.table.get_item(Key={'hostname': hostname},
                                  ConsistentRead=consistent_read,
                                  ReturnConsumedCapacity='NONE')
        logger.debug('Record: %s', item)
        try:
            return cls(**schema.load(item['Item']))
        except KeyError:
            return None

    @classmethod
    def get_all_servers(cls, consistent_read=False):
        logger.info('Fetching all server records')
        schema = cls.schema()
        res = cls.table.scan(
            ReturnConsumedCapacity='NONE',
            ConsistentRead=consistent_read
        )
        return [cls(**schema.load(server)) for server in res.get('Items', [])]

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

    def __repr__(self):
        return f'<BasicServer(name={self.name}, hostname={self.hostname}>'


class LaunchableServer(BasicServer):
    schema = LaunchableServerSchema

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.schema = self.schema()
        if self.status is None or self.status_expired:
            self.update_status()

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
    def launch_time(self) -> typing.Union[datetime, None]:
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

    def update_status(self):
        from schema import ServerStatusSchema, LaunchableServerSchema

        logger.info('Updating MCServer %s', str(self))

        # Grab fresh data with consistent_read to DB
        item = self.table.get_item(Key={'hostname': self.hostname},
                                   ConsistentRead=True,
                                   ReturnConsumedCapacity='NONE')
        logger.debug('DynamoDB Item: %s', item)
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
            self.status = status
        except (ConnectionRefusedError, BrokenPipeError, OSError):
            self.status = status_schema.dump({})
        if self.data['status']['description']['text'] != 'Offline' or not self.launching:
            self.launch_time = None
        self.status_time = datetime.utcnow()
        self.save(safe=False)

    @property
    def status_expired(self):
        if self.status_time is None:
            return True
        return self.status_time + config['SERVER_STATUS_TTL'] < datetime.utcnow()

    @property
    def version(self) -> int:
        try:
            return self.data['version']
        except KeyError as e:
            raise AttributeError from e

    @version.setter
    def version(self, value: int):
        self.data['version'] = value

    def save(self, safe: bool = True):
        logger.info('Saving record for %s, safe=%s', str(self), str(safe))
        version = self.version
        self.version = version + 1
        data = self.schema.dump(self.data)
        logger.info('Updating DB for %s', self.hostname)
        if version > 0 and safe:
            # Optimistic lock via condition - let fail if concurrent updates
            self.table.put_item(Item=data, ConditionExpression=Attr('version').eq(version))
        else:
            self.table.put_item(Item=data)

    def launch(self):
        logger.info('Invoking server launcher function')
        lambda_.invoke(
            FunctionName=config['LAUNCHER_FUNCTION_ARN'],
            InvocationType='Event',
            Payload=json.dumps({
                'server_name': self.name,
                # TODO: look the below values up from new db fields
                'instance_type': 't3.large',
                'volume_size': 20,
                'memory_size': '6144m'
            })
        )
        for i in range(3):
            try:
                self.launch_time = datetime.utcnow()
                self.save(safe=True)
                break
            except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
                logger.info('Concurrent write prevented on attempt %s', i)
                sleep(randint(0, 2**i))
                item = self.table.get_item(Key={'hostname': self.hostname},
                                           ConsistentRead=True,
                                           ReturnConsumedCapacity='NONE')
                self.data.update(**self.schema.load(item['Item']))

    def __repr__(self):
        return f'<LaunchableServer(name={self.name}, hostname={self.hostname}>'
