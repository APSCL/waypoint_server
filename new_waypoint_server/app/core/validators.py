# common validation functions that will be shared between multiple functions

import numpy as np
from app.agvs.constants import AGVState
from app.agvs.models import AGV
from app.commands.constants import CommandTypes
from app.commands.models import Command
from app.tasks.constants import Priority, TaskStatus
from app.tasks.models import Task
from flask import current_app


def validate_2d_coordinates(x, y):
    if (
        x > current_app.config["X_COORD_UPPER_BOUND"]
        or x < current_app.config["X_COORD_LOWER_BOUND"]
    ):
        return False
    if (
        y > current_app.config["Y_COORD_UPPER_BOUND"]
        or y < current_app.config["Y_COORD_LOWER_BOUND"]
    ):
        return False
    return True


def validate_theta(theta):
    if theta < -np.pi or theta > np.pi:
        return False
    return True


def is_valid_task_status(status: str):
    task_statuses = [str(task_status) for task_status in TaskStatus]
    if status not in task_statuses:
        return False
    return True


def is_valid_priority(priority: str):
    priorities = [str(priority) for priority in Priority]
    if priority not in priorities:
        return False
    return True


def is_valid_agv_state(state: str):
    agv_states = [str(agv_state) for agv_state in AGVState]
    if state not in agv_states:
        return False
    return True


def is_valid_command_type(type: str):
    command_types = [str(command_type) for command_type in CommandTypes]
    if type not in command_types:
        return False
    return True


def validate_cancel_agv_command(id_tuple):
    agv_id = id_tuple[0]
    agv = AGV.query.filter_by(id=agv_id).first()
    if agv.status != AGVState.BUSY:
        return False
    return True


def validate_cancel_task_command(id_tuple):
    task_id = id_tuple[1]
    task = Task.query.filter_by(id=task_id).first()
    if task.status != TaskStatus.IN_PROGRESS:
        return False
    return True


def validate_stop_agv_command(id_tuple):
    agv_id = id_tuple[0]
    stop_command_exists = (
        Command.query.filter_by(
            agv_id=agv_id, processed=False, type=CommandTypes.STOP_AGV
        ).order_by(Command.id.asc())
    ).first()
    if stop_command_exists:
        return False
    return True


def validate_start_agv_command(id_tuple):
    agv_id = id_tuple[0]

    agv = AGV.query.filter_by(id=agv_id).first()
    if agv.status != AGVState.STOPPED:
        return False

    start_command_exists = (
        Command.query.filter_by(
            agv_id=agv_id, processed=False, type=CommandTypes.START_AGV
        ).order_by(Command.id.asc())
    ).first()
    if start_command_exists:
        return False
    return True


def validate_command(command_type, agv_id, task_id):
    command_type_to_validation_function = {
        CommandTypes.CANCEL_AGV: validate_cancel_agv_command,
        CommandTypes.CANCEL_TASK: validate_cancel_task_command,
        CommandTypes.STOP_AGV: validate_stop_agv_command,
        CommandTypes.START_AGV: validate_start_agv_command,
    }
    id_tuple = (agv_id, task_id)
    validation_function = command_type_to_validation_function[command_type]
    return validation_function(id_tuple)


def validate_agv_ready_update(data):
    status = data.get("status")
    if status != AGVState.READY:
        return False
    return True


# TODO: Validate data based on which state you're in (READY, BUSY, DONE) for guarantee of data integrity later!
def validate_agv_update_data(agv_state, data):
    agv_state_to_validation_function = {
        AGVState.READY: validate_agv_ready_update,
    }
    validation_function = agv_state_to_validation_function.get(agv_state, None)
    if validation_function is None:
        return True
    return validation_function(data)
