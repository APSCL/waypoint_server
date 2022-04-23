from app import db, ma
from .models import TestModel
from marshmallow import fields, ValidationError

# TODO: This is just an example serializers.py file which will be detached/removed later

class TestModelSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TestModel
        load_instance = True
        sql_session = db.session

    id =  fields.Integer(dump_only=True)
    name = fields.String(required=True)