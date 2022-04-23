from app import db
from .models import TestModel
from flask import make_response, request, current_app, jsonify
from flask_restful import Resource
from .serializers import TestModelSchema
from . import main_api

# TODO: This is just an example views.py file which will be detached/removed later

class TestView(Resource):
    def get(self):
        queryset = TestModel.query.all()
        return make_response(jsonify(TestModelSchema(many=True).dump(queryset)), 200)

    def post(self):
        errors = TestModelSchema().validate(request.form)
        if errors:
            return make_response(jsonify(errors) , 400)
        test_model = TestModelSchema().load(request.form)
        create_test_model(db, test_model)
        return make_response(jsonify(TestModelSchema().dump(test_model)), 201)
        

# TODO - create a utils.py file for db model creation
def create_test_model(db, test_model):
    db.session.add(test_model)
    db.session.commit()  

main_api.add_resource(TestView, "/test_route")
