from app.agvs.constants import AGVState
from app.core import validators
from app.database import db
from app.extentions import ma
from app.tasks.constants import Priority, TaskStatus
from marshmallow import ValidationError, fields, validates_schema
from marshmallow_enum import EnumField

from .models import Task, Waypoint


class WaypointCreateSerializer(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Waypoint
        load_instance = True
        sql_session = db.session

    y = fields.Float(required=True)
    x = fields.Float(required=True)
    visited = fields.Boolean(required=False)
    order = fields.Integer(required=True)

    @validates_schema
    def perform_validation(self, data, **kwargs):
        # perform coordinate validation with respect to the map
        if not validators.validate_2d_coordinates(data.get("x"), data.get("y")):
            raise ValidationError(
                "X or Y coordinate is out of bounds for the allowable range of navigatable coordinates"
            )


class WaypointDetailSerializer(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Waypoint
        load_instance = True
        sql_session = db.session

    id = fields.Integer(dump_only=True)
    y = fields.Float()
    x = fields.Float()
    visited = fields.Boolean()
    order = fields.Integer()


class TaskCreateSerializer(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        load_instance = True
        sql_session = db.session

    status = EnumField(TaskStatus)
    priority = EnumField(Priority, required=False)


class TaskDetailSerializer(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        load_instance = True
        sql_session = db.session

    id = fields.Integer(dump_only=True)
    status = EnumField(TaskStatus)
    priority = EnumField(Priority)
    waypoints = fields.Nested(WaypointDetailSerializer(many=True), dump_only=True)
    agv_id = fields.Integer(dump_only=True)
    num_waypoints = fields.Method("get_num_waypoints", dump_only=True)

    def get_num_waypoints(self, instance):
        return instance.num_waypoints
