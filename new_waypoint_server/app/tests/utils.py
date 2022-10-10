from app.agvs.constants import AGVDriveTrainType, AGVState
from app.agvs.models import AGV
from app.commands.constants import CommandTypes
from app.commands.models import Command
from app.database import db
from app.tasks.constants import Priority, TaskStatus
from app.tasks.models import Task, Waypoint


def unique_id_generator():
    id = 0
    while 1:
        id += 1
        yield id


id_generator = unique_id_generator()
ip_generator = unique_id_generator()


def create_agv(
    id=None,
    ip_address=None,
    status=None,
    power=None,
    x=None,
    y=None,
    theta=None,
    current_task_id=None,
    drive_train_type=None,
    tasks=None,
):
    if id is None:
        id = next(id_generator)
    if ip_address is None:
        ip_address = f"0.0.0.{next(ip_generator)}"
    if x is None:
        x = 0.0
    if y is None:
        y = 0.0
    if theta is None:
        theta = 0.0
    if power is None:
        power = 100
    if status is None:
        status = AGVState.READY
    if drive_train_type is None:
        drive_train_type = AGVDriveTrainType.ACKERMANN

    agv = AGV(
        id=id,
        ip_address=ip_address,
        x=x,
        y=y,
        theta=theta,
        status=status,
        power=power,
        current_task_id=current_task_id,
        drive_train_type=drive_train_type,
    )
    agv.save()

    if tasks is not None:
        for task in tasks:
            agv.tasks.append(task)
            agv.save()

    return agv


def create_task(priority=None, status=None, agv_id=None, drive_train_type=None, waypoints=None):
    if priority is None:
        priority = Priority.MEDIUM
    if status is None:
        status = TaskStatus.INCOMPLETE

    task = Task(
        priority=priority,
        status=status,
        agv_id=agv_id,
        drive_train_type=drive_train_type,
    )
    task.save()

    if waypoints is not None:
        for waypoint in waypoints:
            task.waypoints.append(waypoint)
            task.save()

    return task


def create_waypoint(x=None, y=None, theta=None, order=None, visited=None):
    if x is None:
        x = 0.0
    if y is None:
        y = 0.0
    if theta is None:
        theta = 0.0
    if order is None:
        order = 0
    if visited is None:
        visited = False

    waypoint = Waypoint(x=x, y=y, theta=theta, order=order, visited=visited)
    waypoint.save()

    return waypoint


def create_command(agv_id=None, task_id=None, type=None, processed=None):
    if type is None:
        type = CommandTypes.STOP_AGV
    if processed is None:
        processed = False

    command = Command(agv_id=agv_id, task_id=task_id, type=type, processed=processed)
    command.save()

    return command
