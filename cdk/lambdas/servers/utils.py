
from datetime import datetime
from decimal import Decimal
from functools import wraps
import json
from typing import Callable


from config import logger
from exceptions import MASNotFoundError


class APIEncoder(json.JSONEncoder):
    """
    Custom JSON Encoder that handles Decimal objects
    """
    def default(self, o):
        if isinstance(o, Decimal):
            if o.as_integer_ratio()[1] == 1:
                # This is an integer value
                return int(o)
            else:
                # We're okay with a float approximation
                return float(0)
        if isinstance(o, datetime):
            return o.timestamp()
        return super().default(o)


def api_handler(fn: Callable):
    """
    Common handling of of API Gateway events
    """
    @wraps(fn)
    @logger.inject_lambda_context
    def wrapped(event, context):
        event['headers'].pop('Authorization', None)
        event['multiValueHeaders'].pop('Authorization', None)

        logger.info('Processing call', path=event['path'], method=event['httpMethod'])
        logger.debug('Event', event=event)
        try:
            return {
                'statusCode': 200,
                'body': json.dumps(fn(event, context), cls=APIEncoder)
            }
        except MASNotFoundError as e:
            logger.info('Resource not found', exc_info=e)
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'Not found'})
            }
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error('Error processing request', exc_info=e)
            return {
                'statusCode': 500,
                'body': json.dumps({'message': 'Internal error'})
            }
    return wrapped
