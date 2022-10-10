import sys

from app.agvs.constants import AGVState
from app.agvs.models import AGV
from app.commands.constants import CommandTypes
from app.commands.models import Command
from app.commands.serializers import CommandSerializer
from app.core import validators
from app.task_scheduler.scheduler import TASK_SCHEDULER_MAP
from app.tasks.constants import TaskStatus
from app.tasks.models import Task, Waypoint
from app.tasks.serializers import TaskDetailSerializer
from flask import current_app
from flask_api import status


class CommandProcessingController:
    @classmethod
    def _retrieve_all_relavent_commands_query(cls, agv):
        agv_commands = (
            Command.query.filter_by(processed=False, agv_id=agv.id).order_by(Command.id.asc())
        ).all()
        task_commands = (
            Command.query.filter_by(processed=False, task_id=agv.current_task_id).order_by(
                Command.id.asc()
            )
        ).all()
        result = agv_commands + task_commands
        return list(sorted(result, key=lambda command: command.id))

    @classmethod
    def _retrieve_stop_agv_command(cls, agv):
        # returns the latest STOP command
        stop_commands = (
            Command.query.filter_by(
                agv_id=agv.id, processed=False, type=CommandTypes.STOP_AGV
            ).order_by(Command.id.asc())
        ).all()
        if not stop_commands:
            return None
        return stop_commands[-1]

    @classmethod
    def _retrieve_start_agv_command(cls, agv):
        # returns the latest START command
        start_commands = (
            Command.query.filter_by(
                agv_id=agv.id, processed=False, type=CommandTypes.START_AGV
            ).order_by(Command.id.asc())
        ).all()
        if not start_commands:
            return None
        return start_commands[-1]

    @classmethod
    def _remove_invalid_relavent_commands(cls, agv):
        # process all relavent commands to be in a "valid state", removal occurs by marking the command as "processed"
        commands = cls._retrieve_all_relavent_commands_query(agv)
        if not commands:
            return
        for command in commands:
            command_type, agv_id, task_id = command.type, command.agv_id, command.task_id
            valid_command = validators.validate_command(command_type, agv_id, task_id)
            if not valid_command:
                command.update(processed=True)
                command.save()

    @classmethod
    def get_next_command(cls, agv):
        commands = cls._retrieve_all_relavent_commands_query(agv)
        if not commands:
            return None

        # process stop and start commands first, they take precedence
        latest_start_command, latest_stop_command = cls._retrieve_start_agv_command(
            agv
        ), cls._retrieve_stop_agv_command(agv)
        if latest_stop_command:
            return latest_stop_command
        if latest_start_command:
            return latest_start_command

        # reaching here means we have not detected a start or stop command, we also guarantee that all commands will be relavent with command creation validation
        cls._remove_invalid_relavent_commands(agv)
        updated_commands = cls._retrieve_all_relavent_commands_query(agv)
        if not updated_commands:
            return None
        return updated_commands[0]

    @classmethod
    def process_command(cls, agv, command):
        command.update(processed=True)
        command_type_to_process_function = {
            CommandTypes.CANCEL_AGV: cls.process_cancel_agv_or_task,
            CommandTypes.CANCEL_TASK: cls.process_cancel_agv_or_task,
            CommandTypes.STOP_AGV: cls.process_stop_agv,
            CommandTypes.START_AGV: cls.process_start_agv,
        }
        process_funciton = command_type_to_process_function[command.type]
        process_funciton(agv)
        return True, None, CommandSerializer().dump(command)

    @classmethod
    def process_cancel_agv_or_task(cls, agv):
        task = Task.query.filter_by(id=agv.current_task_id).first()
        for waypoint in task.waypoints:
            waypoint.update(visited=False)
            waypoint.save()
        task.update(status=TaskStatus.INCOMPLETE)
        task.save()
        agv.update(current_task_id=None, status=AGVState.READY)
        agv.save()

    @classmethod
    def process_stop_agv(cls, agv):
        # "cancel" the current task the AGV is processing (however, the AGV may be in the ready state)
        task = Task.query.filter_by(id=agv.current_task_id).first()
        if task is not None:
            for waypoint in task.waypoints:
                waypoint.update(visited=False)
                waypoint.save()
            task.update(status=TaskStatus.INCOMPLETE)
            task.save()

        # place the AGV into the "Stop" Loop
        agv.update(current_task_id=None, status=AGVState.STOPPED)
        agv.save()

        # remove all other commands for the AGV
        commands = cls._retrieve_all_relavent_commands_query(agv)
        for command in commands:
            command.update(processed=True)

    @classmethod
    def process_start_agv(cls, agv):
        agv.update(current_task_id=None, status=AGVState.READY)


class AGVUpdateController:
    @classmethod
    def update_agv(cls, data):
        agv_id, agv_status = data.get("id"), data.get("status")
        agv = AGV.query.filter_by(id=agv_id).first()

        # process commands first, and if none immediately exist, execute an update action
        command = CommandProcessingController.get_next_command(agv)
        if command is not None:
            (
                process_sucessful,
                command_debug_message,
                command_json,
            ) = CommandProcessingController.process_command(agv, command)
            return process_sucessful, command_debug_message, command_json

        state_to_update_function = {
            AGVState.READY: cls.update_agv_ready,
            AGVState.BUSY: cls.update_agv_busy,
            AGVState.DONE: cls.update_agv_done,
            AGVState.STOPPED: cls.update_agv_stopped,
        }
        update_function = state_to_update_function[agv_status]
        update_successful, update_debug_message, update_output_json = update_function(agv, data)
        return update_successful, update_debug_message, update_output_json

    @classmethod
    def _basic_agv_state_update(cls, agv, data):
        x, y, theta, agv_status = (
            data.get("x"),
            data.get("y"),
            data.get("theta"),
            data.get("status"),
        )
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
        return True, None, None

    @classmethod
    def update_agv_busy(cls, agv, data):
        # TODO: consider adding validation: account for factors like current task_id is not the one registered to the agv?
        cls._basic_agv_state_update(agv, data)
        task_id, waypoint_order = data.get("current_task_id"), data.get(
            "current_waypoint_order", sys.maxsize
        )
        task = Task.query.filter_by(id=task_id).first()

        visited_waypoints = Waypoint.query.filter_by(task_id=task.id, visited=False).filter(
            Waypoint.order < waypoint_order
        )
        for waypoint in visited_waypoints:
            waypoint.update(visited=True)
            waypoint.save()

        return True, None, None

    @classmethod
    def update_agv_done(cls, agv, data):
        cls._basic_agv_state_update(agv, data)
        task_id = data.get("current_task_id")
        task = Task.query.filter_by(id=task_id).first()

        # mark all task waypoints as visited
        for waypoint in task.waypoints:
            waypoint.update(visited=True)
            waypoint.save()
        # update task to be complete
        task.update(status=TaskStatus.COMPLETE)
        task.save()
        # set agv current task to be none
        agv.update(current_task_id=None)
        agv.save()

        return True, None, None

    @classmethod
    def update_agv_stopped(cls, agv, data):
        # Do nothing here, we want to lock the AGV from doing anything
        cls._basic_agv_state_update(agv, data)
        return True, None, None


class TaskAssignmentController:
    @classmethod
    def get_task_for_agv(cls, data):
        agv_status = data.get("status")
        if agv_status is not AGVState.READY:
            return status.HTTP_400_BAD_REQUEST, {
                "message": "AGV must be in the READY state, to recieve a task"
            }

        scheduler_key = current_app.config["TASK_SCHEDULER"]
        scheduler = TASK_SCHEDULER_MAP.get(scheduler_key, None)
        if not scheduler:
            return status.HTTP_400_BAD_REQUEST, {
                "message": f"Unable to fetch task, problem with task scheudling algorithm: {scheduler_key}"
            }

        agv = AGV.query.filter_by(id=data.get("id")).first()

        tasks = cls.retrieve_relavent_tasks(agv)

        task = scheduler.generate_optimal_assignment(agv, tasks)

        if task is None:
            return status.HTTP_202_ACCEPTED, {"message": "No tasks available at this time"}

        cls._register_task_to_agv(agv, task)
        return status.HTTP_200_OK, TaskDetailSerializer().dump(task)

    @classmethod
    def retrieve_relavent_tasks(cls, agv):
        # get tasks that were directly assigned to the requesting agv
        agv_assigned_tasks = Task.query.filter_by(
            status=TaskStatus.INCOMPLETE, agv_id=agv.id
        ).all()

        # get tasks associated with the drive train of the agv that were not directly assigned to the agv
        drive_train_assigned_tasks = Task.query.filter_by(
            status=TaskStatus.INCOMPLETE, agv_id=None, drive_train_type=agv.drive_train_type
        ).all()

        # get all tasks that are neither possess an assigned drive train or assigned agv
        general_tasks = Task.query.filter_by(
            status=TaskStatus.INCOMPLETE, agv_id=None, drive_train_type=None
        ).all()
        tasks = agv_assigned_tasks + drive_train_assigned_tasks + general_tasks
        return tasks

    @classmethod
    def _register_task_to_agv(cls, agv, task):
        task.update(status=TaskStatus.IN_PROGRESS)
        agv.update(current_task_id=task.id, status=AGVState.BUSY)
        agv.tasks.append(task)
        agv.save()
