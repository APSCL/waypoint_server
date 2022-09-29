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
    def _get_queryset(self):
        return Command.query

    # TODO: Consider filtering all commands by all of its fields (might help!)
    def get(self):
        queryset = self._get_queryset().all()
        if not queryset:
            return make_response(jsonify([]), status.HTTP_200_OK)
        serializer = CommandSerializer(many=True)
        data = serializer.dump(queryset)
        return make_response(jsonify(data), status.HTTP_200_OK)

    def delete(self):
        commands = self._get_queryset().all()
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
                jsonify({"message": "Command was not registered within the waypoint server"}), status.HTTP_202_ACCEPTED
            )
        command.delete()
        return make_response(jsonify({"message": "Command successfully deleted"}), status.HTTP_200_OK)


commands_api.add_resource(CommandCreateView, "/")
commands_api.add_resource(CommandDetailView, "/<int:id>/")
commands_api.add_resource(CommandListView, "/commands/")
