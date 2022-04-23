from flask import Blueprint
from flask_restful import Api

pings = Blueprint("pings", __name__)
pings_api = Api(pings)

from . import views