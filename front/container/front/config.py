import json
import os
from datetime import timedelta
import uuid

basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig(object):
    """Base configuration."""

    APP_NAME = os.getenv("APP_NAME", "launcher")
    SERVER_DOMAIN = os.environ['SERVER_DOMAIN']
    LAUNCHER_TASK_ARN = os.environ['LAUNCHER_TASK_ARN']
    LAUNCHER_NETWORK_CONFIG = json.loads(os.environ['LAUNCHER_NETWORK_CONFIG'])
    CLUSTER_ARN = os.environ['CLUSTER_ARN']
    BCRYPT_LOG_ROUNDS = 4
    DEBUG_TB_ENABLED = False
    SECRET_KEY = os.getenv("SECRET_KEY", str(uuid.uuid4()))
    WTF_CSRF_ENABLED = False
    TOKEN_TTL = timedelta(hours=1)
    SERVER_STATUS_TTL = timedelta(seconds=30)
    LAUNCHER_TIMEOUT = timedelta(minutes=10)


class DevelopmentConfig(BaseConfig):
    """Development configuration."""

    DEBUG = True
    DEBUG_TB_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False


class TestingConfig(BaseConfig):
    """Testing configuration."""

    PRESERVE_CONTEXT_ON_EXCEPTION = False
    TESTING = True


class ProductionConfig(BaseConfig):
    """Production configuration."""

    BCRYPT_LOG_ROUNDS = 13
    WTF_CSRF_ENABLED = True
