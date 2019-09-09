from flask import Blueprint, request
from flask_restful import Resource, Api, abort
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from launcher import db
from launcher.auth import auth_required
from launcher.servers.models import LaunchableServer
from launcher.servers.schema import LaunchableServerSchema

servers_blueprint = Blueprint('servers', __name__)
api = Api(servers_blueprint)


class LaunchableServerView(Resource):
    @auth_required('user')
    def get(self, server_id: int = None):
        """
        Get server data

        :param int server_id: (Optional) Server id requested
        :return: Server(s) requested
        """
        if server_id is not None:
            server = LaunchableServer.query.get(server_id)
            if server is None:
                abort(404)
            schema = LaunchableServerSchema()
        else:
            servers = LaunchableServer.query.order_by(LaunchableServer.name).all()
            schema = LaunchableServerSchema(many=True)
        result = schema.dump(servers)
        # Save any status updates
        db.session.commit()
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
            db.session.add(new_server)
            db.session.commit()
        except IntegrityError:
            return {'error': 'duplicate server data'}
        except SQLAlchemyError as e:
            return {'error': str(e.__class__.__name__)}
        return schema.dump(new_server)


api.add_resource(LaunchableServerView, '/<int:server_id>', '/', endpoint='servers')
