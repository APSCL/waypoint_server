from app import db
from flask import request, jsonify, make_response
from flask_restful import Resource
from flask_api import status
from . import pings_api

class TestConnectionView(Resource):
    def get(self):
        return make_response(
            jsonify({"message":"request received"}), 
            status.HTTP_200_OK
        )

pings_api.add_resource(TestConnectionView, "/test_connection/")
