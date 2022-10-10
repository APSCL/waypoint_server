from app.agvs.constants import AGVState
from app.agvs.models import AGV
from app.core import validators
from app.extentions import ma
from app.tasks.constants import Priority, TaskStatus
from marshmallow import ValidationError, fields, pre_load, validates_schema
from marshmallow_enum import EnumField


class AGVUpdateSerializer(ma.Schema):
    id = fields.Integer(required=True)
    status = EnumField(AGVState, required=True)
    x = fields.Float(required=True)
    y = fields.Float(required=True)
    theta = fields.Float(required=True)
    current_task_id = fields.Integer(required=False)
    current_waypoint_order = fields.Integer(required=False)

    @pre_load
    def remove_has_default_key_if_none(self, data: dict, **kwargs):
        if data.get("current_task_id") is None:
            data.pop("current_task_id", None)
        if data.get("current_waypoint_order") is None:
            data.pop("current_waypoint_order", None)
        return data

    @validates_schema
    def perform_valdiation(self, data, **kwargs):
        ros_domain_id = data.get("id")
        if not AGV.query.filter_by(id=ros_domain_id).count():
            raise ValidationError("AGV with provided ROS_DOMAIN_ID is not registered!")

        if not validators.validate_2d_coordinates(data.get("x"), data.get("y")):
            raise ValidationError(
                "X or Y coordinate is out of bounds for the allowable range of navigatable coordinates"
            )
        if not validators.validate_theta(data.get("theta")):
            raise ValidationError(
                "theta is out of bounds from the allowable range of values: [-pi, pi]"
            )

        state = self.context.get("state", None)
        if state and not validators.validate_agv_update_data(state, data):
            raise ValidationError(f"Invalid data for AGV:{state} Update")
