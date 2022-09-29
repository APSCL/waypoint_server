from app.commands.serializers import CommandSerializer
from app.tasks.serializers import TaskDetailSerializer
from flask import jsonify, make_response, request
from flask_api import status

# from . import pings_api
from . import agv_request_handlers
from .controllers import AGVUpdateController, TaskAssignmentController
from .serializers import AGVUpdateSerializer


@agv_request_handlers.route("/test_connection/", methods=["GET"])
def handle_ping_waypoint_server():
    return make_response(jsonify({"message": "request received"}), status.HTTP_200_OK)


@agv_request_handlers.route("/request_task/", methods=["GET"])
def handle_new_task_request():
    serializer = AGVUpdateSerializer()
    data = request.get_json()
    errors = serializer.validate(data)
    if errors:
        return make_response(jsonify(errors), status.HTTP_400_BAD_REQUEST)
    validated_data = serializer.load(data)

    status_code, response_data = TaskAssignmentController.get_task_for_agv(validated_data)

    return make_response(jsonify(response_data), status_code)

    # get the request task request - simply return the AGV id and coordindates (use update serializer)
    # serialize/validate data then shoot it into the TaskAssignment Controller
    # handle the request, like making sure that all pseudo tasks are turned into tasks before hand!
    # retieve the assigned task, update it by marking as in progress, assign it to the agv, update agv current_task id
    # succeed!


def create_update_status_response(success, debug_message, data):
    return {
        "update_successful": success,
        "debug_message": debug_message,
        "command": data,
    }


@agv_request_handlers.route("/update_state/", methods=["POST"])
def handle_agv_update_state():
    serializer = AGVUpdateSerializer()
    data = request.get_json()
    errors = serializer.validate(data)
    if errors:
        return make_response(jsonify(errors), status.HTTP_400_BAD_REQUEST)
    validated_data = serializer.load(data)
    update_successful, update_debug_message, update_json = AGVUpdateController.update_agv(validated_data)
    response = create_update_status_response(update_successful, update_debug_message, update_json)
    if not update_successful:
        return make_response(jsonify(response), status.HTTP_400_BAD_REQUEST)

    # TODO: parse commands and send as a handshake to the AGV
    return make_response(jsonify(response), status.HTTP_200_OK)

    # get the update and serialize that the update is a okay
    # if the agv is in the done state (write flexibly):
    #   - mark the last waypoint as visited, current task as done and agv current_task id as complete, put AGV in the ready state
    # if the agv is busy (write flexibly - maybe the AGV is in a command!):
    #   - either is on a different waypoint than the last, mark the last as visited (or don't)
    # parse commands and send as a handshake to the AGV
