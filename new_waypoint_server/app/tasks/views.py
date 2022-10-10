from collections import defaultdict

import app.core.validators as validators
from app.database import db
from flask import current_app, jsonify, make_response, request
from flask_api import status
from flask_restful import Resource

from . import tasks_api
from .constants import Priority, TaskStatus
from .models import Task, Waypoint
from .serializers import (
    TaskCreateSerializer,
    TaskDetailSerializer,
    WaypointCreateSerializer,
)


class TaskCreateView(Resource):
    def _validate_waypoints(self, data):
        waypoints = data.get("waypoints", None)
        if not waypoints:
            return {"error": "No valid waypoints provided"}

        # perform validation on each provided waypoint
        serializer = WaypointCreateSerializer()
        order_uniqueness_identifier = defaultdict(lambda: 0)
        for waypoint in waypoints:
            errors = serializer.validate(waypoint)
            if errors:
                return {"error": errors}
            order_uniqueness_identifier[waypoint.get("order")] += 1

        if len(order_uniqueness_identifier) != len(waypoints):
            return {
                "error": "Ordering of waypoints provided invalid - repetition in order detected"
            }

    def _create_task_waypoints(self, task, waypoints):
        serializer = WaypointCreateSerializer()
        for waypoint in waypoints:
            waypoint = serializer.load(waypoint, session=db.session)
            task.waypoints.append(waypoint)
            task.save()

    def post(self):
        serializer = TaskCreateSerializer()
        data = request.get_json()
        errors = self._validate_waypoints(data)
        if errors:
            return make_response(jsonify(errors), status.HTTP_400_BAD_REQUEST)

        waypoints = data.pop("waypoints")
        task = serializer.load(data, session=db.session)
        task.save()
        self._create_task_waypoints(task, waypoints)

        return make_response(jsonify(TaskDetailSerializer().dump(task)), status.HTTP_201_CREATED)


class TaskListView(Resource):
    def _query_parameters_valid(self, priority, status):
        if priority is not None and not validators.is_valid_priority(priority):
            return False
        if status is not None and not validators.is_valid_task_status(status):
            return False
        return True

    def _get_filtered_task_queryset(self, priority, status):
        # priority and status are guaranteed to be valid at this point
        filter_kwargs = {}
        if priority is not None:
            filter_kwargs["priority"] = priority
        if status is not None:
            filter_kwargs["status"] = status
        return Task.query.filter_by(**filter_kwargs).all()

    def get(self):
        query_status, query_priority = request.args.get("status", None), request.args.get(
            "priority", None
        )
        if not self._query_parameters_valid(query_priority, query_status):
            return make_response(
                jsonify({"message": "Invalid query parameters"}), status.HTTP_400_BAD_REQUEST
            )

        queryset = self._get_filtered_task_queryset(query_priority, query_status)
        if not queryset:
            return make_response(jsonify([]), status.HTTP_200_OK)
        task_list_fields = ("id", "priority", "status", "agv_id")
        serializer = TaskDetailSerializer(many=True, only=task_list_fields)
        data = serializer.dump(queryset)
        return make_response(jsonify(data), status.HTTP_200_OK)

    def delete(self):
        tasks = Task.query.all()
        if not tasks:
            return make_response(
                jsonify({"message": "No Tasks currently exist to delete"}),
                status.HTTP_202_ACCEPTED,
            )

        for task in tasks:
            task.delete()

        return make_response(
            jsonify({"message": "All Tasks successfully deleted"}), status.HTTP_200_OK
        )


class TaskDetailView(Resource):
    def _get_queryset(self):
        return Task.query

    def get(self, id):
        queryset = self._get_queryset().filter_by(id=id).first()
        if not queryset:
            return make_response(
                jsonify(
                    {"message": f"Task does not exist within the waypoint server"},
                ),
                status.HTTP_400_BAD_REQUEST,
            )
        serializer = TaskDetailSerializer()
        data = serializer.dump(queryset)
        return make_response(jsonify(data), status.HTTP_200_OK)

    def delete(self, id):
        task = self._get_queryset().filter_by(id=id).first()
        if task is None:
            return make_response(
                jsonify({"message": "Task does not exist within the waypoint server"}),
                status.HTTP_400_BAD_REQUEST,
            )
        task.delete()
        return make_response(jsonify({"message": "AGV successfully deleted"}), status.HTTP_200_OK)


tasks_api.add_resource(TaskCreateView, "/")
tasks_api.add_resource(TaskDetailView, "/<int:id>/")
tasks_api.add_resource(TaskListView, "/tasks/")
