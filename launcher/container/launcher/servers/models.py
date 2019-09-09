from datetime import datetime

from flask import current_app
from mcstatus import MinecraftServer

from launcher import db


class LaunchableServer(db.Model):

    __tablename__ = 'launchable_servers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    hostname = db.Column(db.String(255), unique=True, nullable=False)
    _status = db.Column(db.String(524288))
    status_time = db.Column(db.DateTime)

    @property
    def status(self):
        from .schema import ServerStatusSchema

        schema = ServerStatusSchema()

        if self._status is None or self.status_expired:
            self.update_status()
        return schema.loads(self._status)

    @status.setter
    def status(self, new_status):
        from .schema import ServerStatusSchema

        schema = ServerStatusSchema()
        self._status = schema.dumps(new_status)

    def update_status(self):
        from .schema import ServerStatusSchema

        current_app.logger.info('Updating MCServer %s', str(self))

        if not hasattr(self, '_server'):
            self._server = MinecraftServer.lookup(self.hostname)
        schema = ServerStatusSchema()
        try:
            status = self._server.status()
            self._status = schema.dumps(status)
            self.status_time = datetime.utcnow()
        except (ConnectionRefusedError, BrokenPipeError, OSError):
            self._status = schema.dumps({})
            self.status_time = datetime.utcnow()
        return self._status


    @property
    def status_expired(self):
        return self.status_time + current_app.config['SERVER_STATUS_TTL'] < datetime.utcnow()

    def __repr__(self):
        return f'<LaunchableServer(name={self.name}, hostname={self.hostname}>'
