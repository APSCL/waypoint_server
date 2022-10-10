from app.agvs.constants import AGVState
from flask import jsonify, make_response, request
from flask_api import status

from . import agv_request_handlers
from .controllers import AGVUpdateController, TaskAssignmentController
from .serializers import AGVUpdateSerializer


@agv_request_handlers.route("/test_connection/", methods=["GET"])
def handle_ping_waypoint_server():
    return make_response(jsonify({"message": "request received"}), status.HTTP_200_OK)


@agv_request_handlers.route("/request_task/", methods=["GET"])
def handle_new_task_request():
    serializer = AGVUpdateSerializer(context={"state": AGVState.READY})
    data = request.get_json()
    errors = serializer.validate(data)
    if errors:
        return make_response(jsonify(errors), status.HTTP_400_BAD_REQUEST)
    validated_data = serializer.load(data)

    status_code, response_data = TaskAssignmentController.get_task_for_agv(validated_data)

    return make_response(jsonify(response_data), status_code)


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
    update_successful, update_debug_message, update_output_json = AGVUpdateController.update_agv(
        validated_data
    )
    response = {
        "update_successful": update_successful,
        "debug_message": update_debug_message,
        "command": update_output_json,
    }

    if not update_successful:
        return make_response(jsonify(response), status.HTTP_400_BAD_REQUEST)

    return make_response(jsonify(response), status.HTTP_200_OK)
