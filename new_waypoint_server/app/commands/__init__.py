from flask import Blueprint
from flask_restful import Api

commands = Blueprint("commands", __name__)
commands_api = Api(commands)

from . import views
