import json
import logging
import os
from datetime import timedelta

import boto3


class Config(dict):
    def pull_configs(self):
        ssm = boto3.client('ssm')
        self['LAUNCHER_NETWORK_CONFIG'] = json.loads(ssm.get_parameter(
            Name=self['LAUNCHER_NETWORK_CONFIG_PARAMETER'],
            WithDecryption=False
        )['Parameter']['Value'])


config = Config({
    'APP_NAME': os.getenv("APP_NAME", "launcher"),
    'SERVER_DOMAIN': os.environ['SERVER_DOMAIN'],
    'DYNAMODB_SERVERS_TABLE_NAME': os.environ['DYNAMODB_SERVERS_TABLE_NAME'],
    'LAUNCHER_TASK_ARN': os.environ['LAUNCHER_TASK_ARN'],
    'LAUNCHER_NETWORK_CONFIG_PARAMETER': os.environ['LAUNCHER_NETWORK_CONFIG_PARAMETER'],
    'CLUSTER_ARN': os.environ['CLUSTER_ARN'],
    'SERVER_STATUS_TTL': timedelta(seconds=30),
    'LAUNCHER_TIMEOUT': timedelta(minutes=10),
    'DEBUG': True,
})

logger = logging.getLogger(config['APP_NAME'])
logging.basicConfig()
logger.setLevel(logging.DEBUG if config['DEBUG'] else logging.INFO)
