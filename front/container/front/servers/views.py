from flask import Blueprint, request, current_app
from flask_restful import Resource, Api, abort
from marshmallow import ValidationError

from front.auth import auth_required
from front.servers.models import LaunchableServer
from front.servers.schema import LaunchableServerSchema

servers_blueprint = Blueprint('servers', __name__)
api = Api(servers_blueprint)


class LaunchableServerView(Resource):
    @auth_required('user')
    def get(self, hostname: str = None):
        """
        Get server data

        :param str hostname: (Optional) Server name requested
        :return: Server(s) requested
        """
        if hostname is not None:
            server = LaunchableServer.get_server_by_hostname(hostname)
            if server is None:
                abort(404)
            result = server.data
            server.save()
        else:
            servers = LaunchableServer.get_all_servers()
            for s in servers:
                s.save()
            result = [server.data for server in servers]
        # current_app.logger.debug('Sending response: %s', result)
        return result

    @auth_required('admin')
    def post(self, hostname: str = None):
        """
        Add a server

        :param str hostname: Not used
        :return:
        """
        schema = LaunchableServerSchema()
        try:
            new_server = schema.load(request.json)
        except ValidationError as e:
            return e.messages, 400

        try:
            new_server.save()
        except Exception:
            return {'error': 'duplicate server data'}
        return schema.dump(new_server)

    @auth_required('user')
    def put(self, hostname: str):
        """
        Update or perform an action on a server
        :param str hostname: Server name to update / act on
        :return: Server
        """
        server = LaunchableServer.get_server_by_hostname(hostname)
        if server is None:
            abort(404)
        server.launch()
        schema = LaunchableServerSchema()
        return schema.dump(server)


api.add_resource(LaunchableServerView, '/<hostname>', '/', endpoint='servers')
