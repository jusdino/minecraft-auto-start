from __future__ import annotations

import json
from collections import UserDict
from datetime import UTC, datetime
from random import randint
from time import sleep

import boto3
from boto3.dynamodb.conditions import Attr
from mcstatus import JavaServer

from config import config, logger
from exceptions import MASNotFoundError
from schema.basic_server import BasicServerSchema
from schema.java_server_raw_status import JavaServerRawStatusSchema
from schema.launchable_server import LaunchableServerSchema

dynamodb = boto3.resource('dynamodb')
lambda_ = boto3.client('lambda')


class BasicServer(UserDict):
    table = dynamodb.Table(config.dynamodb_servers_table_name)
    schema = BasicServerSchema()
    status_schema = JavaServerRawStatusSchema()

    @classmethod
    def _get_db_record(cls, hostname, consistent_read=False):
        return cls.table.get_item(
            Key={'hostname': hostname},
            ConsistentRead=consistent_read,
            ReturnConsumedCapacity='NONE'
        )

    @classmethod
    def get_server_by_hostname(cls, hostname, consistent_read=False):
        logger.info('Fetching record for %s', hostname)
        item = cls._get_db_record(hostname, consistent_read)
        logger.debug('Record for %s: %s', hostname, item)
        try:
            server = cls.schema.load(item['Item'])
            return cls(server)
        except KeyError as e:
            raise MASNotFoundError(f'{hostname} not found') from e

    @classmethod
    def get_all_servers(cls, consistent_read=False):
        logger.info('Fetching all server records')
        res = cls.table.scan(
            ReturnConsumedCapacity='NONE',
            ConsistentRead=consistent_read
        )

        # Deserialize the records
        servers = [cls.schema.load(server) for server in res.get('Items', [])]
        # Instantiate server objects
        return [cls(**server) for server in servers]

    @property
    def status_expired(self):
        return self.data['status_time'] < (datetime.now(tz=UTC) - config.server_status_ttl)

    def update_if_expired(self):
        """
        Update status if our in-memory status is expired
        """
        if self.status_expired:
            self.update_from_db()
        # If the status from the DB is not fresh, get status from the actual server
        if self.status_expired:
            self.update_status()

    def update_from_db(self):
        logger.info('Updating MCServer %s from database', str(self), hostname=self.data['hostname'])

        # Grab fresh data with consistent_read to DB
        item = self.table.get_item(
            Key={'hostname': self.data['hostname']},
            ConsistentRead=True,
            ReturnConsumedCapacity='NONE'
        )
        logger.debug('DynamoDB Item: %s', item)
        try:
            self.data = self.schema.load(item['Item'])
        except KeyError:
            return

    def update_status(self):
        logger.info('Updating MCServer %s status', str(self), hostname=self.data['hostname'])

        if not hasattr(self, '_server'):
            self._server = JavaServer.lookup(self.data['hostname'])

        try:
            # Check status by connecting to the server
            status = self._server.status().raw
            logger.debug('Server raw status: %s', status, hostname=self.data['hostname'])
            # Deserialize the status in a way we've customized
            status = self.status_schema.load(status)
            self.data.update({
                'online': True,
                'description': status['description'],
                'players': status['players'],
                'mc_version': status['version'],
                'favicon': status.get('favicon')
            })
        except (ConnectionRefusedError, BrokenPipeError, OSError) as e:
            # Server is not running
            logger.info('Could not contact server: %s', e, hostname=self.data['hostname'])
            self.data['online'] = False
            self.data['players'] = {'max': 0, 'online': 0}
        logger.debug('Updated status', online=self.data['online'], hostname=self.data['hostname'])

        # Save new status to DB
        self.data['status_time'] = datetime.now(tz=UTC)
        self.save(safe=False)

    def save(self, safe: bool = True):
        prev_version = self.data['version']
        self.data['version'] += 1
        data = self.schema.dump(self.data)
        logger.info('Updating DB', hostname=self.data['hostname'], data=data, prev_version=prev_version)
        if prev_version > 0 and safe:
            # Optimistic lock via condition - let fail if concurrent updates
            self.table.put_item(Item=data, ConditionExpression=Attr('version').eq(prev_version))
        else:
            self.table.put_item(Item=data)

    def __repr__(self):
        return f'BasicServer(name={self.data['name']}, hostname={self.data['hostname']})'


class LaunchableServer(BasicServer):
    schema = LaunchableServerSchema()

    @staticmethod
    def server_is_launching(data: dict):
        return data['launch_time'] > (datetime.now(tz=UTC) - config.launcher_timeout)

    @property
    def launching(self) -> bool:
        return self.server_is_launching(self.data)

    def launch(self):
        logger.info('Invoking server launcher function', hostname=self.data['hostname'])
        for i in range(3):
            try:
                # We'll treat successfully writing our data to the DB sort of like acquiring a lock on the process
                # to launch the server
                self.data['launch_time'] = datetime.now(tz=UTC)
                self.save(safe=True)
                payload = {
                    'server_name': self.data['name']
                }
                if 'instance_configuration' in self.data:
                    payload['instance_configuration'] = self.data['instance_configuration']
                lambda_.invoke(
                    FunctionName=config.launcher_function_arn,
                    InvocationType='Event',
                    Payload=json.dumps(payload)
                )
                break
            except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
                logger.info('Concurrent write prevented on attempt %s', i, hostname=self.data['hostname'])
                sleep(randint(0, 2**i))
                self.update_from_db()

    def update_status(self):
        # Logging online/offline status
        super().update_status()
        launch_time = self.data['launch_time']
        if self.data.get('online', False) is True:
            logger.info(
                'Server is online, %s minutes after last launch',
                (datetime.now(tz=UTC) - launch_time).total_seconds() / 60,
                hostname=self.data['hostname']
            )
        elif not self.launching:
            logger.info(
                'Server is offline, %s minutes after last launch',
                (datetime.now(tz=UTC) - launch_time).total_seconds() / 60,
                hostname=self.data['hostname']
            )
        self.data['launching'] = self.launching

    def __repr__(self):
        return f'LaunchableServer(name={self.data['name']}, hostname={self.data['hostname']})'
