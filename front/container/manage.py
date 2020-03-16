#!/usr/bin/env python

from getpass import getpass
from flask.cli import FlaskGroup

from front import create_app
from front.auth.models import FullUser

app = create_app()
cli = FlaskGroup(create_app=create_app)


@cli.command()
def create_user():
    """Creates the admin user."""
    email = input('Email: ')
    password = getpass('Password: ')
    FullUser(email=email, password=password, admin=False).save()


@cli.command()
def create_admin():
    """Creates the admin user."""
    email = input('Email: ')
    password = getpass('Password: ')
    FullUser(email=email, password=password, admin=True).save()


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
