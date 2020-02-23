from flask import Blueprint, request
from flask_restful import Resource, Api, abort
from marshmallow import ValidationError

from front.auth import auth_required
from front.servers.models import LaunchableServer
from front.servers.schema import LaunchableServerSchema

servers_blueprint = Blueprint('servers', __name__)
api = Api(servers_blueprint)


class LaunchableServerView(Resource):
    @auth_required('user')
    def get(self, hostname: int = None):
        """
        Get server data

        :param int hostname: (Optional) Server id requested
        :return: Server(s) requested
        """
        if hostname is not None:
            server = LaunchableServer.get_server_by_hostname(hostname)
            if server is None:
                abort(404)
            schema = LaunchableServerSchema()
            result = schema.dump(server)
            server.save()
        else:
            servers = LaunchableServer.get_all_servers()
            schema = LaunchableServerSchema(many=True)
            result = schema.dump(servers)
            for s in servers:
                s.save()
        return result

    @auth_required('admin')
    def post(self, server_id: int = None):
        """
        Add a server

        :param server_id: Not used
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


api.add_resource(LaunchableServerView, '/<hostname>', '/', endpoint='servers')
