from app.agvs.constants import AGVState
from app.agvs.models import AGV
from app.core import validators
from app.database import db
from app.extentions import ma
from app.tasks.constants import TaskStatus
from app.tasks.models import Task
from marshmallow import ValidationError, fields, pre_load, validates_schema
from marshmallow_enum import EnumField

from .constants import CommandTypes
from .models import Command


class CommandSerializer(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Command
        load_instance = True
        sql_session = db.session

    id = fields.Integer(dump_only=True)
    processed = fields.Integer(dump_only=True)
    agv_id = fields.Integer()
    task_id = fields.Integer()
    type = EnumField(CommandTypes)

    @pre_load
    def remove_has_default_key_if_none(self, data: dict, **kwargs):
        if data.get("agv_id") is None:
            data.pop("agv_id", None)
        if data.get("task_id") is None:
            data.pop("task_id", None)
        return data

    def _command_is_agv_related(self, command_type):
        agv_related_commands = [
            CommandTypes.START_AGV,
            CommandTypes.STOP_AGV,
            CommandTypes.CANCEL_AGV,
        ]
        if command_type in agv_related_commands:
            return True
        return False

    def _command_is_task_related(self, command_type):
        task_related_commands = [CommandTypes.CANCEL_TASK]
        if command_type in task_related_commands:
            return True
        return False

    @validates_schema
    def perform_validation(self, data, **kwargs):
        command_type, task_id, agv_id = (
            data.get("type"),
            data.get("task_id"),
            data.get("agv_id", None),
        )

        if task_id is None and agv_id is None:
            raise ValidationError("Command provided without and AGV or Task ID")

        if task_id is not None and agv_id is not None:
            raise ValidationError("Command cannot be created with both a AGV a Task ID")

        # TODO: Consider adding a check if the "agv_id" maps to an existing AGV object within the database
        if self._command_is_agv_related(command_type) and agv_id is None:
            raise ValidationError("AGV Command Type provided with no valid AGV ID")

        # TODO: Consider adding a check if the "task_id" maps to an existing AGV object within the database
        if self._command_is_task_related(command_type) and task_id is None:
            raise ValidationError("Task Command Type provided with no valid Task ID")

        if agv_id is not None and AGV.query.filter_by(id=agv_id).count() == 0:
            raise ValidationError("AGV with provided id not found!")

        if task_id is not None and Task.query.filter_by(id=task_id).count() == 0:
            raise ValidationError("Task with provided id not found!")

        agv = AGV.query.filter_by(id=agv_id).first()
        if (
            agv is not None
            and command_type != CommandTypes.START_AGV
            and agv.status == AGVState.STOPPED
        ):
            raise ValidationError(
                "AGV cannot accept new commands (except for START_AGV) while it is stopped!"
            )

        # TODO: Add validation against commands that are not pertinent, ie)
        # don't allow a cancelation task to be created for a task not currently being processed

        if not validators.validate_command(command_type, agv_id, task_id):
            raise ValidationError(f"Invalid creation for command: {command_type}")
