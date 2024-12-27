from models import BasicServer, LaunchableServer
from utils import api_handler
from config import logger


@api_handler
def get_servers(event, context):
    return [server.data for server in BasicServer.get_all_servers()]


@api_handler
def get_one_server(event, context):
    hostname = event['pathParameters']['hostname']
    server = LaunchableServer.get_server_by_hostname(hostname)
    server.update_if_expired()
    server['launching'] = server.launching
    return server.data


@api_handler
def launch_server(event, context):
    hostname = event['pathParameters']['hostname']
    server = LaunchableServer.get_server_by_hostname(hostname, consistent_read=True)
    if not server.launching:
        server.launch()
    else:
        logger.info('Server is already launching', hostname=hostname)
    return server.data
