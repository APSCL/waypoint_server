from collections import defaultdict

from app.agvs.constants import AGVState
from app.core import validators
from app.database import db
from app.extentions import ma
from app.tasks.constants import Priority, TaskStatus
from app.tasks.models import Task, Waypoint
from marshmallow import ValidationError, fields, validates_schema
from marshmallow_enum import EnumField

from .models import AGV


class AGVCreateSerializer(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = AGV
        load_instance = True
        sql_session = db.session

    id = fields.Integer(required=True)
    ip_address = fields.String(required=False)
    status = EnumField(AGVState, required=False)
    power = fields.Integer()
    x = fields.Float(required=True)
    y = fields.Float(required=True)
    theta = fields.Float(required=True)

    # TODO: Complete Validation
    @validates_schema
    def perform_validation(self, data, **kwargs):
        ros_domain_id = data.get("id")
        if AGV.query.filter_by(id=ros_domain_id).count():
            raise ValidationError("AGV with provided ROS_DOMAIN_ID already registered!")

        x, y, theta = data.get("x"), data.get("y"), data.get("theta")
        if not validators.validate_2d_coordinates(x, y):
            raise ValidationError("X or Y coordinate is out of the allowable range of coordinates")
        if not validators.validate_theta(theta):
            raise ValidationError("theta is out of bounds from the allowable range of values: [-pi, pi]")


class AGVDetailSerializer(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = AGV
        load_instance = True
        sql_session = db.session

    _limited_task_fields = ("id", "status", "priority")

    id = fields.Integer(dump_only=True)
    ip_address = fields.String(dump_only=True)
    status = EnumField(AGVState, dump_only=True)
    power = fields.Int(dump_only=True)
    x = fields.Float(dump_only=True)
    y = fields.Float(dump_only=True)
    theta = fields.Float(dump_only=True)
    # tasks = fields.Nested(TaskDetailSerializer(many=True, only=_limited_task_fields), dump_only=True)
    current_task_id = fields.Integer(dump_only=True)

class AGVUpdateSerializer(ma.SQLAlchemyAutoSchema):
    id = fields.Integer(required=True)
    x = fields.Float(required=True)
    y = fields.Float(required=True)
    theta = fields.Float(required=True)
    status = EnumField(AGVState)
    current_task_id = fields.Integer(required=True)
    current_waypoint_order = fields.Integer(required=False)

    # TODO: Complete Validation
    @validates_schema
    def perform_validation(self, data, **kwargs):
        agv_id = data.get("id")
        if not AGV.query.filter_by(id=agv_id).first().exists():
            raise ValidationError("AGV is not registered within the waypoint server")

        x, y, theta = data.get("theta"), data.get("theta"), data.get("theta")
        if not validators.validate_2d_coordinates(x, y):
            raise ValidationError("X or Y coordinate is out of the allowable range of coordinates")
        if not validators.validate_theta(theta):
            raise ValidationError("theta is out of bounds from the allowable range of values: [-pi, pi]")

        current_task = Task.query.filter_by(id=data.get("current_task_id")).first()
        if not current_task.exists():
            raise ValidationError("Task is not registered within the waypoint server")
        order_points = [waypoint.order for waypoint in current_task.waypoints]
        
        current_waypoint_order = data.get("current_waypoint_order", None)
        if current_waypoint_order is not None and (current_waypoint_order > max(order_points) or current_waypoint_order < min(current_waypoint_order)):
            raise ValidationError("Current Waypoint order provided does not exist within the waypoints registered under the current task")
