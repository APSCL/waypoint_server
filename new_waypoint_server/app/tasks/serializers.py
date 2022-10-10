from app.agvs.constants import AGVDriveTrainType
from app.agvs.models import AGV
from app.core import validators
from app.database import db
from app.extentions import ma
from app.tasks.constants import Priority, TaskStatus
from marshmallow import ValidationError, fields, pre_load, validates_schema
from marshmallow_enum import EnumField

from .models import Task, Waypoint


class WaypointCreateSerializer(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Waypoint
        load_instance = True
        sql_session = db.session

    x = fields.Float(required=True)
    y = fields.Float(required=True)
    theta = fields.Float(required=False)
    visited = fields.Boolean(required=False)
    order = fields.Integer(required=True)

    @pre_load
    def remove_has_default_key_if_none(self, data: dict, **kwargs):
        if data.get("theta") is None:
            data.pop("theta", None)
        return data

    @validates_schema
    def perform_validation(self, data, **kwargs):
        if not validators.validate_2d_coordinates(data.get("x"), data.get("y")):
            raise ValidationError(
                "X or Y coordinate is out of bounds for the allowable range of navigatable coordinates"
            )

        theta = data.get("theta", None)
        if theta and not validators.validate_theta(theta):
            raise ValidationError(
                "theta is out of bounds from the allowable range of values: [-pi, pi]"
            )


class WaypointDetailSerializer(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Waypoint
        load_instance = True
        sql_session = db.session

    id = fields.Integer(dump_only=True)
    x = fields.Float()
    y = fields.Float()
    theta = fields.Float()
    visited = fields.Boolean()
    order = fields.Integer()


class TaskCreateSerializer(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        load_instance = True
        sql_session = db.session

    status = EnumField(TaskStatus)
    priority = EnumField(Priority, required=False)
    drive_train_type = EnumField(AGVDriveTrainType, required=False)
    agv_id = fields.Integer(required=False)

    @validates_schema
    def perform_validation(self, data, **kwargs):
        agv_id = data.get("agv_id", None)
        if agv_id is not None and AGV.query.filter_by(id=agv_id).first() is None:
            raise ValidationError("Unable to create task assigned to unregistered AGV")


class TaskDetailSerializer(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        load_instance = True
        sql_session = db.session

    id = fields.Integer(dump_only=True)
    status = EnumField(TaskStatus)
    priority = EnumField(Priority)
    drive_train_type = EnumField(AGVDriveTrainType)
    waypoints = fields.Nested(WaypointDetailSerializer(many=True), dump_only=True)
    agv_id = fields.Integer(dump_only=True)
    num_waypoints = fields.Method("get_num_waypoints", dump_only=True)

    def get_num_waypoints(self, instance):
        return instance.num_waypoints
