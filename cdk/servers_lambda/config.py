import logging
import os
from datetime import timedelta


class Config(dict):
    pass


config = Config({
    'APP_NAME': os.getenv("APP_NAME", "servers"),
    'SUB_DOMAIN': os.environ['SUB_DOMAIN'],
    'DYNAMODB_SERVERS_TABLE_NAME': os.environ['DYNAMODB_SERVERS_TABLE_NAME'],
    'LAUNCHER_FUNCTION_ARN': os.environ['LAUNCHER_FUNCTION_ARN'],
    'SERVER_STATUS_TTL': timedelta(seconds=30),
    'LAUNCHER_TIMEOUT': timedelta(minutes=10),
    'DEBUG': True,
})

logger = logging.getLogger(config['APP_NAME'])
logging.basicConfig()
logger.setLevel(logging.DEBUG if config['DEBUG'] else logging.INFO)
