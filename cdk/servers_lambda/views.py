import json
import logging

from marshmallow import ValidationError

from models import LaunchableServer
from schema import LaunchableServerSchema


logging.basicConfig()
logger = logging.getLogger()
logger.level = logging.DEBUG


def servers(event, context):
    logger.debug('Received event: %s', json.dumps(event))
    if event['httpMethod'] == 'GET':
        return Servers.get(event)
    if event['httpMethod'] == 'PUT':
        return Servers.put(event)
    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }

def server(event, context):
    logger.debug(f'Received server event: %s', json.dumps(event))
    hostname = event['pathParameters']['hostname']
    if event['httpMethod'] == 'GET':
        return Servers.get(event, hostname)
    if event['httpMethod'] == 'PUT':
        return Servers.put(event, hostname)


class Servers():
    @staticmethod
    def get(event, hostname: str = None):
        """
        Get server data
        """
        if hostname is not None:
            server = LaunchableServer.get_server_by_hostname(hostname)
            if server is None:
                return {'statusCode': 404, 'body': ''}
            result = server.data
        else:
            servers = LaunchableServer.get_all_servers()
            result = [server.data for server in servers]
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }

    @staticmethod
    def post(event):
        """
        Add a server
        """
        schema = LaunchableServerSchema()
        try:
            new_server = LaunchableServer(**schema.load(json.loads(event['body'])))
            new_server.save()
        except ValidationError as e:
            return e.messages, 400

        return schema.dump(new_server)

    @staticmethod
    def put(event, hostname: str = None):
        """
        Update or perform an action on a server
        """
        server = LaunchableServer.get_server_by_hostname(hostname, consistent_read=True)
        if server is None:
            return {'statusCode': 404}
        server.launch()
        schema = LaunchableServerSchema()
        return schema.dump(server)
