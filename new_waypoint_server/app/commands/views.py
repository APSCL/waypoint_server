from app.core import validators
from app.database import db
from flask import current_app, jsonify, make_response, request
from flask_api import status
from flask_restful import Resource

from . import commands_api
from .models import Command
from .serializers import CommandSerializer


class CommandCreateView(Resource):
    def post(self):
        serializer = CommandSerializer()
        data = request.form.to_dict()
        errors = serializer.validate(data)
        if errors:
            return make_response(jsonify(errors), status.HTTP_400_BAD_REQUEST)
        command = serializer.load(data, session=db.session)
        command.save()
        return make_response(jsonify(CommandSerializer().dump(command)), status.HTTP_201_CREATED)


class CommandListView(Resource):
    def _query_parameters_valid(self, type):
        if type is not None and not validators.is_valid_command_type(type):
            return False
        return True

    def _get_filtered_task_queryset(self, agv_id, task_id, type, processed):
        filter_kwargs = {}
        if agv_id is not None:
            filter_kwargs["agv_id"] = agv_id
        if task_id is not None:
            filter_kwargs["task_id"] = task_id
        if type is not None:
            filter_kwargs["type"] = type
        if processed is not None:
            filter_kwargs["processed"] = processed
        return Command.query.filter_by(**filter_kwargs).all()

    def get(self):
        agv_id, task_id, type, processed = (
            request.args.get("agv_id", None),
            request.args.get("task_id", None),
            request.args.get("type", None),
            request.args.get("processed", None),
        )
        queryset = self._get_filtered_task_queryset(agv_id, task_id, type, processed)
        if not queryset:
            return make_response(jsonify([]), status.HTTP_200_OK)
        serializer = CommandSerializer(many=True)
        data = serializer.dump(queryset)
        return make_response(jsonify(data), status.HTTP_200_OK)

    def delete(self):
        commands = Command.query.all()
        if not commands:
            return make_response(
                jsonify({"message": "No Commands currently exist to delete"}), status.HTTP_202_ACCEPTED
            )

        for command in commands:
            command.delete()

        return make_response(jsonify({"message": "All Commands successfully deleted"}), status.HTTP_200_OK)


class CommandDetailView(Resource):
    def _get_queryset(self):
        return Command.query

    def get(self, id):
        queryset = self._get_queryset().filter_by(id=id).first()
        if not queryset:
            return make_response(
                jsonify(
                    {"message": f"Command with ID={id} is not registered within the waypoint server"},
                ),
                status.HTTP_400_BAD_REQUEST,
            )
        serializer = CommandSerializer()
        data = serializer.dump(queryset)
        return make_response(jsonify(data), status.HTTP_200_OK)

    # TODO: Consider a different method for deletion for a command (considering if it already being processed by an AGV)
    def delete(self, id):
        command = self._get_queryset().filter_by(id=id).first()
        if command is None:
            return make_response(
                jsonify({"message": "Command was not registered within the waypoint server"}),
                status.HTTP_400_BAD_REQUEST,
            )
        command.delete()
        return make_response(jsonify({"message": "Command successfully deleted"}), status.HTTP_200_OK)


commands_api.add_resource(CommandCreateView, "/")
commands_api.add_resource(CommandDetailView, "/<int:id>/")
commands_api.add_resource(CommandListView, "/commands/")
