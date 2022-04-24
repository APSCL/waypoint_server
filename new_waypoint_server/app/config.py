import os
from enum import Enum

from dotenv import load_dotenv

load_dotenv()

# Config for Internal Development
class DevelopmentConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", None)
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///server.db")
    PORT = int(os.environ.get("PORT", 5000))
    # HOST = os.environ.get("HOST", "0.0.0.0")
    # TODO: Change this back to being hosted on local host after development
    HOST = "0.0.0.0"
    X_COORD_LOWER_BOUND = 0
    X_COORD_UPPER_BOUND = 11
    Y_COORD_LOWER_BOUND = 0
    Y_COORD_UPPER_BOUND = 11
    TASK_SCHEDULER = "GREEDY_SJF"
    PATH_PLANNER = "BASIC"
    MAP = "2D_SIMULATION"


# Config for Deployed Sever
class DeploymentConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", None)
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///server.db")
    PORT = int(os.environ.get("PORT", 5000))
    HOST = "0.0.0.0"
    X_COORD_LOWER_BOUND = 0
    X_COORD_UPPER_BOUND = 11
    Y_COORD_LOWER_BOUND = 0
    Y_COORD_UPPER_BOUND = 11
    TASK_SCHEDULER = "GREEDY_SJF"
    PATH_PLANNER = "BASIC"
    MAP = "2D_SIMULATION"


# Config for Internal Testing
class TestingConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", None)
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    PORT = int(os.environ.get("PORT", 5000))
    HOST = "127.0.0.1"
    X_COORD_LOWER_BOUND = 0
    X_COORD_UPPER_BOUND = 11
    Y_COORD_LOWER_BOUND = 0
    Y_COORD_UPPER_BOUND = 11
    TASK_SCHEDULER = "GREEDY_SJF"
    PATH_PLANNER = "BASIC"
    MAP = "2D_SIMULATION"


class ConfigType(Enum):
    TESTING = TestingConfig
    DEVELOPMENT = DevelopmentConfig
    DEPLOYMENT = DeploymentConfig
