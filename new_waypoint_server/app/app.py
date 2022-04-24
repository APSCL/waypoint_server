import click
from flask import Flask
from flask.cli import with_appcontext

import app.commands as commands
from app.config import ConfigType, DeploymentConfig, DevelopmentConfig, TestingConfig
from app.extentions import db, ma, migrate


def create_app(conf_type=ConfigType.DEVELOPMENT):
    app = Flask(__name__)
    # sync config
    initialize_config(app, conf_type)
    # set up all flask extensions
    initialize_extensions(app)
    # register routes and blueprints
    register_blueprints(app)
    # set up logging within the app to track recieved requests etc
    configure_logging(app)
    # set up flask cli commands
    register_commands(app)

    return app


def initialize_config(app, conf_type):
    conf_dict = {conf.name: conf.value for conf in ConfigType}
    conf_class = conf_dict.get(conf_type.name, DevelopmentConfig)
    app.config.from_object(conf_class)
    # disable warnings
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


# TODO: Set up error_handlers, possibly (could just do validation purely from within backend)
def register_error_handlers(app):
    pass


# TODO: Set up logging for the APP
def configure_logging(app):
    pass


def initialize_database(app):
    with app.app_context():
        # db.drop_all()
        from app.agvs.models import AGV
        from app.tasks.models import Task, Waypoint
        db.create_all()
        db.session.commit()


def register_commands(app):
    app.cli.add_command(commands.init_db)
    app.cli.add_command(commands.test)
