import app.cli_commands as cli_commands
import click
from app.config import ConfigType, DeploymentConfig, DevelopmentConfig, TestingConfig
from app.extentions import db, ma, migrate
from flask import Flask
from flask.cli import with_appcontext


def create_app(conf_type=ConfigType.DEVELOPMENT):
    app = Flask(__name__)
    # sync config
    initialize_config(app, conf_type)
    # set up all flask extensions
    initialize_extensions(app)
    # register routes and blueprints
    register_blueprints(app)
    # set up flask cli commands
    register_commands(app)

    return app


def initialize_config(app, conf_type):
    conf_dict = {conf.name: conf.value for conf in ConfigType}
    conf_class = conf_dict.get(conf_type.name, DevelopmentConfig)
    app.config.from_object(conf_class)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


def initialize_extensions(app):
    db.init_app(app)
    initialize_database(app)
    ma.init_app(app)
    migrate.init_app(app, db)


def register_blueprints(app):
    from app.agvs import agvs

    app.register_blueprint(agvs, url_prefix="/agvs")

    from app.tasks import tasks

    app.register_blueprint(tasks, url_prefix="/tasks")

    from app.agv_request_handlers import agv_request_handlers

    app.register_blueprint(agv_request_handlers, url_prefix="/agv_request_handlers")

    from app.commands import commands

    app.register_blueprint(commands, url_prefix="/commands")


# TODO: Consider configuring Waypoint Server error handling through Flask: https://flask.palletsprojects.com/en/2.2.x/errorhandling/, however this is likely not needed
def register_error_handlers(app):
    pass


# TODO: Consider configuring Waypoint Server logging through Flask: https://flask.palletsprojects.com/en/2.2.x/errorhandling/, however this is likely not needed
def configure_logging(app):
    pass


def initialize_database(app):
    from app.agvs.models import AGV
    from app.commands.models import Command
    from app.tasks.models import Task, Waypoint

    with app.app_context():
        # db.drop_all()
        db.create_all()
        db.session.commit()


def register_commands(app):
    app.cli.add_command(cli_commands.init_db)
    app.cli.add_command(cli_commands.test)
