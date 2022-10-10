from app.core import validators
from app.database import db
from flask import current_app, jsonify, make_response, request
from flask_api import status
from flask_restful import Resource

from . import agvs_api
from .controllers import PoseAssignmentController
from .models import AGV
from .serializers import AGVCreateSerializer, AGVDetailSerializer


class AGVCreateView(Resource):
    def post(self):
        serializer = AGVCreateSerializer()
        data = request.form.to_dict()
        data["ip_address"] = request.remote_addr
        errors = serializer.validate(data)
        if errors:
            return make_response(jsonify(errors), status.HTTP_400_BAD_REQUEST)
        agv = serializer.load(data, session=db.session)
        agv.save()

        # TODO: Add Pose Assignment / Coordinate Standarization
        # PoseAssignmentController.perform_pose_assignment(agv)

        return make_response(jsonify(AGVDetailSerializer().dump(agv)), status.HTTP_201_CREATED)


class AGVListView(Resource):
    def _query_parameters_valid(self, agv_state):
        if agv_state is not None and not validators.is_valid_agv_state(agv_state):
            return False
        return True

    def _get_filtered_task_queryset(self, agv_state):
        filter_kwargs = {}
        if agv_state is not None:
            filter_kwargs["status"] = agv_state
        return AGV.query.filter_by(**filter_kwargs).all()

    def get(self):
        agv_state = request.args.get("status", None)
        queryset = self._get_filtered_task_queryset(agv_state)
        if not queryset:
            return make_response(jsonify([]), status.HTTP_200_OK)
        serializer = AGVDetailSerializer(many=True)
        data = serializer.dump(queryset)
        return make_response(jsonify(data), status.HTTP_200_OK)

    def delete(self):
        agvs = AGV.query.all()
        if not agvs:
            return make_response(
                jsonify({"message": "No AGVs currently exist to delete"}), status.HTTP_202_ACCEPTED
            )

        for agv in agvs:
            agv.delete()

        return make_response(
            jsonify({"message": "All AGVs successfully deleted"}), status.HTTP_200_OK
        )


class AGVDetailView(Resource):
    def _get_queryset(self):
        return AGV.query

    def get(self, id):
        queryset = self._get_queryset().filter_by(id=id).first()
        if not queryset:
            return make_response(
                jsonify(
                    {
                        "message": "AGV with ROS_DOMAIN_ID is not registered within the waypoint server"
                    },
                ),
                status.HTTP_400_BAD_REQUEST,
            )
        serializer = AGVDetailSerializer()
        data = serializer.dump(queryset)
        return make_response(jsonify(data), status.HTTP_200_OK)

    def delete(self, id):
        agv = self._get_queryset().filter_by(id=id).first()
        if agv is None:
            return make_response(
                jsonify(
                    {
                        "message": "AGV with ROS_DOMAIN_ID is not registered within the waypoint server"
                    }
                ),
                status.HTTP_400_BAD_REQUEST,
            )
        agv.delete()
        return make_response(jsonify({"message": "AGV successfully deleted"}), status.HTTP_200_OK)


agvs_api.add_resource(AGVCreateView, "/")
agvs_api.add_resource(AGVDetailView, "/<int:id>/")
agvs_api.add_resource(AGVListView, "/agvs/")
