import os
import json
import logging

from aws_lambda_powertools import Logger


class Config():
    aws_region = os.environ['AWS_DEFAULT_REGION']
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'

    @property
    def environment_name(self):
        return os.environ['ENV']

    @property
    def tags(self):
        return json.loads(os.environ['TAGS'])

    @property
    def key_name(self):
        return os.environ['SSH_KEY_NAME']

    @property
    def hosted_zone_id(self):
        return os.environ['HOSTED_ZONE_ID']

    @property
    def sub_domain(self):
        return os.environ['SUB_DOMAIN']

    @property
    def data_bucket_id(self):
        return os.environ['DATA_BUCKET_ID']

    @property
    def security_group_id(self):
        return os.environ['SECURITY_GROUP_ID']

    @property
    def subnet_id(self):
        return os.environ['SUBNET_ID']

    @property
    def instance_profile_arn(self):
        return os.environ['INSTANCE_PROFILE_ARN']


logger = Logger()
logging.basicConfig()

if Config.debug:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
