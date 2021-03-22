import json
import os
from datetime import timedelta
import uuid

basedir = os.path.abspath(os.path.dirname(__file__))


config = {
    'APP_NAME': os.getenv("APP_NAME", "launcher"),
    # 'SERVER_DOMAIN': os.environ['SERVER_DOMAIN'],
    'DYNAMODB_SERVERS_TABLE_NAME': os.environ['DYNAMODB_SERVERS_TABLE_NAME'],
    # 'LAUNCHER_TASK_ARN': os.environ['LAUNCHER_TASK_ARN'],
    # 'LAUNCHER_NETWORK_CONFIG': json.loads(os.environ['LAUNCHER_NETWORK_CONFIG']),
    # 'CLUSTER_ARN': os.environ['CLUSTER_ARN'],
    'SECRET_KEY': os.getenv("SECRET_KEY", str(uuid.uuid4())),
    'TOKEN_TTL': timedelta(hours=1),
    'SERVER_STATUS_TTL': timedelta(seconds=30),
    'LAUNCHER_TIMEOUT': timedelta(minutes=10),
    'DEBUG': True,
    'DEBUG_TB_ENABLED': True,
    'DEBUG_TB_INTERCEPT_REDIRECTS': False,
    'PRESERVE_CONTEXT_ON_EXCEPTION': False,
    'TESTING': True,
    'BCRYPT_LOG_ROUNDS': 13
}
