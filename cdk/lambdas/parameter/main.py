import os

from boto3 import client


ssm = client('ssm')
parameter_name = os.environ['USER_POOL_PARAMETER']


def main(event, context):
    value = ssm.get_parameter(
        Name=parameter_name,
        WithDecryption=False
    )['Parameter']['Value']
    return {
        'statusCode': 200,
        'body': value
    }
