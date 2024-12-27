import logging
import os
from datetime import timedelta
from aws_lambda_powertools import Logger


class Config(dict):
    aws_region = os.environ['AWS_DEFAULT_REGION']
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'

    def __init__(self):
        self.app_name = os.getenv("APP_NAME", "servers")
        self.sub_domain = os.environ['SUB_DOMAIN']
        self.dynamodb_servers_table_name = os.environ['DYNAMODB_SERVERS_TABLE_NAME']
        self.launcher_function_arn = os.environ['LAUNCHER_FUNCTION_ARN']
        self.server_status_ttl = timedelta(seconds=30)
        self.launcher_timeout = timedelta(minutes=15)


logger = Logger()
logging.basicConfig()
logger.setLevel(logging.DEBUG if Config.debug else logging.INFO)

config = Config()
