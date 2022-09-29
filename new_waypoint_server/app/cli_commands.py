import os
import unittest

import click
from flask import current_app

import app

from .extentions import db


@click.command()
def test():
    loader = unittest.TestLoader()
    test_dir = f"{os.path.dirname(app.__file__)}/tests"
    suite = loader.discover(test_dir)
    runner = unittest.TextTestRunner()
    runner.run(suite)


@click.command()
def init_db():
    with current_app.app_context():
        db.drop_all()
        db.create_all()
        db.session.commit()

