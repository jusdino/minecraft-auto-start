import json
from datetime import datetime
from random import randint
from time import sleep
import typing

import boto3
from boto3.dynamodb.conditions import Attr
from mcstatus import JavaServer

from schema import BasicServerSchema, LaunchableServerSchema
from config import Config, logger


config = Config()

dynamodb = boto3.resource('dynamodb')
lambda_ = boto3.client('lambda')


class BasicServer():
    table = dynamodb.Table(config.dynamodb_servers_table_name)
    schema = BasicServerSchema

    def __init__(self, **kwargs):
        self.data = dict(**kwargs)
        if not self.data.get('hostname', False):
            self.data['hostname'] = f"{self.data['name']}.{config.sub_domain}"

    @classmethod
    def get_server_by_hostname(cls, hostname, consistent_read=False):
        logger.info('Fetching record for %s', hostname)
        schema = cls.schema()
        item = cls.table.get_item(Key={'hostname': hostname},
                                  ConsistentRead=consistent_read,
                                  ReturnConsumedCapacity='NONE')
        logger.debug('Record for %s: %s', hostname, item)
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
            logger.debug('Setting launch time to None', hostname=self.hostname)
            self.data['launch_time'] = None
            return
        logger.debug('Setting launch time to %s', value, hostname=self.hostname)
        self.data['launch_time'] = str(value.timestamp())

    @property
    def launching(self) -> bool:
        if self.launch_time is None:
            return False
        return self.launch_time + config.launcher_timeout > datetime.utcnow()

    def update_status(self):
        from schema import ServerStatusSchema, LaunchableServerSchema

        logger.info('Updating MCServer %s', str(self), hostname=self.hostname)

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
            self._server = JavaServer.lookup(self.hostname)
        status_schema = ServerStatusSchema()
        try:
            status = self._server.status().raw
            logger.debug('Server raw status: %s', status, hostname=self.hostname)
            status = status_schema.dump(status)
            self.status = status
        except (ConnectionRefusedError, BrokenPipeError, OSError) as e:
            logger.info('Could not contact server: %s', e, hostname=self.hostname)
            self.status = status_schema.dump({})
        logger.debug('Updated status to: %s', self.status, hostname=self.hostname)
        launch_time = self.launch_time
        if self.data['status']['description']['text'] != 'Offline':
            logger.info('Server is online', hostname=self.hostname)
            if launch_time is not None:
                logger.info('Server live after %s seconds',
                            (datetime.utcnow() - launch_time).total_seconds(),
                            hostname=self.hostname)
            self.launch_time = None
        elif not self.launching:
            logger.info('Server is offline', hostname=self.hostname)
            if launch_time is not None:
                logger.info('Server not live after %s seconds',
                            (datetime.utcnow() - launch_time).total_seconds(),
                            hostname=self.hostname)
            self.launch_time = None
        self.status_time = datetime.utcnow()
        self.save(safe=False)

    @property
    def status_expired(self):
        if self.status_time is None:
            return True
        return self.status_time + config.server_status_ttl < datetime.utcnow()

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
        logger.info('Saving record for %s, safe=%s', str(self), str(safe), hostname=self.hostname)
        version = self.version
        self.version = version + 1
        data = self.schema.dump(self.data)
        logger.info('Updating DB', hostname=self.hostname)
        if version > 0 and safe:
            # Optimistic lock via condition - let fail if concurrent updates
            self.table.put_item(Item=data, ConditionExpression=Attr('version').eq(version))
        else:
            self.table.put_item(Item=data)

    def launch(self):
        logger.info('Invoking server launcher function', hostname=self.hostname)
        payload = {
            'server_name': self.name
        }
        if 'instance_configuration' in self.data:
            payload['instance_configuration'] = self.data['instance_configuration']
        lambda_.invoke(
            FunctionName=config.launcher_function_arn,
            InvocationType='Event',
            Payload=json.dumps(payload)
        )
        for i in range(3):
            try:
                self.launch_time = datetime.utcnow()
                self.save(safe=True)
                break
            except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
                logger.info('Concurrent write prevented on attempt %s', i, hostname=self.hostname)
                sleep(randint(0, 2**i))
                item = self.table.get_item(Key={'hostname': self.hostname},
                                           ConsistentRead=True,
                                           ReturnConsumedCapacity='NONE')
                self.data.update(**self.schema.load(item['Item']))

    def __repr__(self):
        return f'<LaunchableServer(name={self.name}, hostname={self.hostname}>'
