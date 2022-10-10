import os
import unittest

import app
import click
from flask import current_app

from .extentions import db


@click.command()
def test():
    """Flask CLI command to run Waypoint Server unit tests"""
    loader = unittest.TestLoader()
    test_dir = f"{os.path.dirname(app.__file__)}/tests"
    suite = loader.discover(test_dir)
    runner = unittest.TextTestRunner()
    runner.run(suite)


@click.command()
def init_db():
    """Flask CLI command to reset the database"""
    with current_app.app_context():
        db.drop_all()
        db.create_all()
        db.session.commit()
