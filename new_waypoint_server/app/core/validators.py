# common validation functions that will be shared between multiple functions

import numpy as np
from app.agvs.constants import AGVState
from app.tasks.constants import Priority, TaskStatus
from flask import current_app


def validate_2d_coordinates(x, y):
    if x > current_app.config["X_COORD_UPPER_BOUND"] or x < current_app.config["X_COORD_LOWER_BOUND"]:
        return False
    if y > current_app.config["Y_COORD_UPPER_BOUND"] or y < current_app.config["Y_COORD_LOWER_BOUND"]:
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
    task_statuses = [str(task_status) for task_status in Priority]
    if priority not in task_statuses:
        return False
    return True


def is_valid_agv_state(state: str):
    task_statuses = [str(task_status) for task_status in AGVState]
    if state not in task_statuses:
        return False
    return True
