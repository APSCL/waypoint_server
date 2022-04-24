import sys

from app.agvs.constants import AGVState
from app.agvs.models import AGV
from app.core import validators
from app.task_scheduler.scheduler import TASK_SCHEDULER_MAP
from app.tasks.constants import TaskStatus
from app.tasks.models import PseudoTask, Task, Waypoint
from app.tasks.serializers import TaskDetailSerializer
from flask import current_app
from flask_api import status


class AGVUpdateController:
    @classmethod
    def update_agv(cls, data):
        agv_id, agv_status = data.get("id"), data.get("status")
        agv = AGV.query.filter_by(id=agv_id).first()
        state_to_update_function = {
            AGVState.READY: cls.update_agv_ready,
            AGVState.BUSY: cls.update_agv_busy,
            AGVState.DONE: cls.update_agv_done,
        }
        update_function = state_to_update_function[agv_status]
        update_successful, update_debug_message = update_function(agv, data)
        return update_successful, update_debug_message

    @classmethod
    def _basic_agv_state_update(cls, agv, data):
        x, y, theta, agv_status = data.get("x"), data.get("y"), data.get("theta"), data.get("status")
        agv.update(
            x=x,
            y=y,
            theta=theta,
            status=agv_status,
        )

    @classmethod
    def update_agv_ready(cls, agv, data):
        # we have a route which handles an AGV being in the READY state, so we don't need to handle that here
        cls._basic_agv_state_update(agv, data)
        return True, None

    @classmethod
    def update_agv_busy(cls, agv, data):
        # TODO: account for factors like current task_id is not the one registered to the agv?
        cls._basic_agv_state_update(agv, data)
        task_id, waypoint_order = data.get("current_task_id"), data.get("current_waypoint_order", sys.maxsize)
        task = Task.query.filter_by(id=task_id).first()

        visited_waypoints = Waypoint.query.filter_by(task_id=task.id, visited=False).filter(
            Waypoint.order < waypoint_order
        )
        for waypoint in visited_waypoints:
            waypoint.update(visited=True)

        return True, None

    @classmethod
    def update_agv_done(cls, agv, data):
        cls._basic_agv_state_update(agv, data)
        task_id = data.get("current_task_id")
        task = Task.query.filter_by(id=task_id).first()
        # mark all task waypoints as visited - TODO: MAYBE CHANGE LATER IF THE COMMAND CANCELED!
        for waypoint in task.waypoints:
            waypoint.update(visited=True)
        task.save()
        # update task to be complete
        task.update(status=TaskStatus.COMPLETE)
        # set agv current task to be none
        agv.update(current_task_id=None)

        return True, None


class TaskAssignmentController:
    @classmethod
    def get_task_for_agv(cls, data):
        agv_status = data.get("status")
        if agv_status is not AGVState.READY:
            return status.HTTP_400_BAD_REQUEST, {"message": "AGV must be in the READY state, to recieve a task"}

        scheduler_key = current_app.config["TASK_SCHEDULER"]
        scheduler = TASK_SCHEDULER_MAP.get(scheduler_key, None)
        if not scheduler:
            return status.HTTP_400_BAD_REQUEST, {
                "message": f"Unable to fetch task, problem with task scheudling algorithm: {scheduler_key}"
            }

        # convert all pseudo tasks into normal tasks - TODO: Complete Pseduo Task System
        pseudo_tasks = PseudoTask.query.all()
        cls._process_all_pseudo_tasks(pseudo_tasks)

        agv = AGV.query.filter_by(id=data.get("id")).first()
        tasks = Task.query.filter_by(status=TaskStatus.INCOMPLETE).all()
        print(tasks)
        task = scheduler.generate_optimal_assignment(agv, tasks)

        if task is None:
            return status.HTTP_202_ACCEPTED, {"message": "No tasks available at this time"}

        cls._register_task_to_agv(agv, task)
        return status.HTTP_200_OK, TaskDetailSerializer().dump(task)

    @classmethod
    def _process_all_pseudo_tasks(cls, pseudo_tasks):
        pass

    @classmethod
    def _register_task_to_agv(cls, agv, task):
        task.update(status=TaskStatus.IN_PROGRESS)
        agv.update(current_task_id=task.id, status=AGVState.BUSY)
        agv.tasks.append(task)
        agv.save()
