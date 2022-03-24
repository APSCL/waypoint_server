from app.config import TestingConfig, DevelopmentConfig, DeploymentConfig, ConfigType
from flask import Flask
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
ma = Marshmallow()
migrate = Migrate()

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
    
    return app

def initialize_config(app, conf_type):
    conf_dict = {conf.name:conf.value for conf in ConfigType}
    conf_class = conf_dict.get(conf_type.name, DevelopmentConfig)
    app.config.from_object(conf_class)

def initialize_extensions(app):
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)

def register_blueprints(app):
    from app.main import main
    app.register_blueprint(main, url_prefix='/main')
    from app.agvs import agvs
    app.register_blueprint(agvs, url_prefix='/agvs')

# TODO: Set up error_handlers, possibly (could just do validation purely from within backend)
def register_error_handlers(app):
    pass

# TODO: Set up logging for the APP
def configure_logging(app):
    pass