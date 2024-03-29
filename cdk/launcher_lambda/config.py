import os
import json
import logging

from aws_lambda_powertools import Logger


class Config():
    aws_region = os.environ['AWS_DEFAULT_REGION']
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'

    def __init__(self):
        self.environment_name = os.environ['ENV']
        self.tags: list = json.loads(os.environ['TAGS'])
        self.key_name = os.environ['SSH_KEY_NAME']
        self.hosted_zone_id = os.environ['HOSTED_ZONE_ID']
        self.sub_domain = os.environ['SUB_DOMAIN']
        self.data_bucket_id = os.environ['DATA_BUCKET_ID']
        self.security_group_id = os.environ['SECURITY_GROUP_ID']
        self.subnet_id = os.environ['SUBNET_ID']
        self.instance_profile_arn = os.environ['INSTANCE_PROFILE_ARN']


logger = Logger()
logging.basicConfig()

if Config.debug:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
