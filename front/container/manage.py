#!/usr/bin/env python

from getpass import getpass
from flask.cli import FlaskGroup

from front import create_app, db
from front.auth.models import User

app = create_app()
cli = FlaskGroup(create_app=create_app)


@cli.command()
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command()
def drop_db():
    """Drops the db tables."""
    db.drop_all()


@cli.command()
def create_user():
    """Creates the admin user."""
    email = input('Email: ')
    password = getpass('Password: ')
    db.session.add(User(email=email, password=password, admin=False))
    db.session.commit()


@cli.command()
def create_admin():
    """Creates the admin user."""
    email = input('Email: ')
    password = getpass('Password: ')
    db.session.add(User(email=email, password=password, admin=True))
    db.session.commit()


@cli.command()
def create_data():
    """Creates sample data."""
    pass


@cli.command()
def get_routes():
    for rule in app.url_map.iter_rules():
        print(rule)


if __name__ == "__main__":
    cli()
