import os
from enum import Enum

from app.core.constants import PoseAssigners
from app.task_scheduler.constants import TaskSchedulers
from dotenv import load_dotenv

load_dotenv()


class DevelopmentConfig:
    """Config for Development Waypoint Server"""

    SECRET_KEY = os.environ.get("SECRET_KEY", None)
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///server.db")
    PORT = int(os.environ.get("PORT", 5000))
    HOST = "0.0.0.0"
    X_COORD_LOWER_BOUND = -1000
    X_COORD_UPPER_BOUND = 1000
    Y_COORD_LOWER_BOUND = -1000
    Y_COORD_UPPER_BOUND = 1000
    TASK_SCHEDULER = TaskSchedulers.GREEDY
    MAP = "2D_SIMULATION"
    # TODO: Add Pose Assignment / Coordinate Standarization
    POSE_ASSIGMENT_METHOD = None


class DeploymentConfig:
    """Config for Deployed Waypoint Server"""

    SECRET_KEY = os.environ.get("SECRET_KEY", None)
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///server.db")
    PORT = int(os.environ.get("PORT", 5000))
    HOST = "0.0.0.0"
    X_COORD_LOWER_BOUND = -1000
    X_COORD_UPPER_BOUND = 1000
    Y_COORD_LOWER_BOUND = -1000
    Y_COORD_UPPER_BOUND = 1000
    TASK_SCHEDULER = TaskSchedulers.GREEDY
    MAP = "2D_SIMULATION"
    # TODO: Add Pose Assignment / Coordinate Standarization
    POSE_ASSIGMENT_METHOD = None


# TODO: Consider deleting this config class, it is practically useless
class TestingConfig:
    """Config for Internal Testing Waypoint Server"""

    SECRET_KEY = os.environ.get("SECRET_KEY", None)
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    PORT = int(os.environ.get("PORT", 5000))
    HOST = "127.0.0.1"
    X_COORD_LOWER_BOUND = 0
    X_COORD_UPPER_BOUND = 11
    Y_COORD_LOWER_BOUND = 0
    Y_COORD_UPPER_BOUND = 11
    TASK_SCHEDULER = TaskSchedulers.GREEDY
    MAP = "2D_SIMULATION"
    # TODO: Add Pose Assignment / Coordinate Standarization
    POSE_ASSIGMENT_METHOD = None


class ConfigType(Enum):
    TESTING = TestingConfig
    DEVELOPMENT = DevelopmentConfig
    DEPLOYMENT = DeploymentConfig
