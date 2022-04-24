from app.agvs.constants import AGVState
from app.agvs.models import AGV
from app.database import db
from app.tasks.constants import Priority, TaskStatus
from app.tasks.models import Task, Waypoint


def create_agv(ip_address=None, status=None, power=None, x=None, y=None, theta=None, current_task_id=None, tasks=None):
    if ip_address is None:
        ip_address = "0.0.0.0"
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

    agv = AGV(ip_address=ip_address, x=x, y=y, status=status, power=power, current_task_id=current_task_id)
    db.session.add(agv)
    db.session.commit()
    return agv


def create_task(starting_waypoint_id=None, priority=None, status=None, agv=None, waypoints=None):
    if starting_waypoint_id is None:
        starting_waypoint_id = -1
    if priority is None:
        priority = Priority.MEDIUM
    if status is None:
        status = TaskStatus.INCOMPLETE

    task = Task(
        starting_waypoint_id=starting_waypoint_id,
        priority=priority,
        status=status,
        agv=agv,
    )

    if waypoints:
        for waypoint in waypoints:
            task.waypoints.append(waypoint)

    db.session.add(task)
    db.session.commit()
    return task


def create_waypoint(x=None, y=None, task=None, next_waypoint=None):
    if x is None:
        x = 0.0
    if y is None:
        y = 0.0

    waypoint = Waypoint(x=x, y=y, task=task, next_waypoint=next_waypoint)

    db.session.add(waypoint)
    db.session.commit(waypoint)
    return waypoint
