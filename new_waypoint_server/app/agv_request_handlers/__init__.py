from flask import Blueprint
from flask_restful import Api

agv_request_handlers = Blueprint("agv_request_handlers", __name__)

from . import views
