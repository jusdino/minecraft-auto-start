import datetime

from flask_bcrypt import generate_password_hash, check_password_hash

from launcher import db


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.registered_on = datetime.datetime.now(tz=datetime.timezone.utc)

    @property
    def password(self):
        """
        For getting purposes, we'll consider password
        and password_hash to be synonymous.
        """
        return self.password_hash

    @password.setter
    def password(self, password):
        """
        Automatically hash passwords before storage
        """
        self.password_hash = generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return check_password_hash(self.password_hash.encode('utf-8'), password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    @property
    def scopes(self):
        if self.admin:
            return ['user', 'admin']
        return ['user']

    @classmethod
    def get_user_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    def __repr__(self):
        return f"<User(id='{self.id}', email='{self.email}')>"
