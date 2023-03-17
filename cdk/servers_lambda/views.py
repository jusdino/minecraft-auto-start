import json

from marshmallow import ValidationError

from config import logger
from models import BasicServer, LaunchableServer
from schema import LaunchableServerSchema


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
    logger.debug('Received server event: %s', json.dumps(event))
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
            servers = BasicServer.get_all_servers()
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
            return {
                'statusCode': 400,
                'body': json.dumps(e.messages)
            }
        return {
            'statusCode': 200,
            'body': schema.dumps(new_server)
        }

    @staticmethod
    def put(event, hostname: str = None):
        """
        Update or perform an action on a server
        """
        server = LaunchableServer.get_server_by_hostname(hostname, consistent_read=True)
        if server is None:
            return {'statusCode': 404}
        if not server.launching:
            server.launch()
        schema = LaunchableServerSchema()
        return {
            'statusCode': 200,
            'body': schema.dumps(server)
        }
