import os
from datetime import datetime, timezone

from flask import current_app
from flask_bcrypt import generate_password_hash, check_password_hash
from boto3.dynamodb.conditions import Attr

from front import dynamodb


def now():
    return datetime.now(tz=timezone.utc)


class User():
    table = dynamodb.Table(os.environ['DYNAMODB_AUTH_TABLE_NAME'])

    @classmethod
    def get_user_by_email(cls, email):
        item = cls.table.get_item(Key={'email': email},
                                  ConsistentRead=True,
                                  ReturnConsumedCapacity='NONE')
        current_app.logger.debug('DynamoDB Item: %s', item)
        try:
            user = cls(**item['Item'])
        except KeyError:
            user = None
        return user

    def __init__(self, **kwargs):
        try:
            password = kwargs.pop('password')
        except KeyError:
            password = None
        self._data = dict(**kwargs)
        if password:
            self.password = password

    @property
    def email(self):
        return self._data['email']

    @email.setter
    def email(self, value):
        self._data['email'] = value

    @property
    def password_hash(self):
        return self._data['password_hash']

    @password_hash.setter
    def password_hash(self, value):
        self._data['password_hash'] = value

    @property
    def registered_on(self):
        return self._data['registered_on']

    @registered_on.setter
    def registered_on(self, value):
        self._data['registered_on'] = value

    @property
    def admin(self):
        return self._data['admin']

    @admin.setter
    def admin(self, value):
        self._data['admin'] = value

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
        return str(self.email)

    @property
    def scopes(self):
        if self.admin:
            return ['user', 'admin']
        return ['user']

    def __repr__(self):
        return f"<User(email='{self.email}')>"

    def save(self):
        version = self._data.get('version', 0)
        self._data['version'] = version + 1
        if version > 0:
            # Optimistic lock via condition - let fail if concurrent updates
            self.table.put_item(Item=self._data, ConditionExpression=Attr('version').eq(version))
        else:
            self.table.put_item(Item=self._data)
