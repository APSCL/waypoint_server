from app.database import db
from flask import current_app, jsonify, make_response, request
from flask_api import status
from flask_restful import Resource

from . import agvs_api
from .models import AGV
from .serializers import AGVCreateSerializer, AGVDetailSerializer, AGVUpdateSerializer


class AGVCreateView(Resource):
    def post(self):
        serializer = AGVCreateSerializer()
        data = request.form.to_dict()
        # add in ip address registration! (might not even need this field)
        data["ip_address"] = request.remote_addr
        errors = serializer.validate(data)
        if errors:
            return make_response(jsonify(errors), status.HTTP_400_BAD_REQUEST)
        agv = serializer.load(data, session=db.session)
        agv.save()
        return make_response(jsonify(AGVDetailSerializer().dump(agv)), status.HTTP_201_CREATED)


class AGVListView(Resource):
    def _get_queryset(self):
        return AGV.query

    def get(self):
        queryset = self._get_queryset().all()
        if not queryset:
            return make_response(jsonify([]), status.HTTP_200_OK)
        serializer = AGVDetailSerializer(many=True)
        data = serializer.dump(queryset)
        return make_response(jsonify(data), status.HTTP_200_OK)

    def delete(self):
        agvs = self._get_queryset().all()
        if not agvs:
            return make_response(jsonify({"message": "No AGVs currently exist to delete"}), status.HTTP_202_ACCEPTED)

        for agv in agvs:
            agv.delete()

        return make_response(jsonify({"message": "All AGVs successfully deleted"}), status.HTTP_200_OK)


class AGVDetailView(Resource):
    def _get_queryset(self):
        return AGV.query
        
    def get(self, id):
        queryset = self._get_queryset().filter_by(id=id).first()
        if not queryset:
            return make_response(
                jsonify(
                    {"message": f"AGV with ROS_DOMAIN_ID={id} is not registered within the waypoint server"},
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
                jsonify({"message": "AGV was not registered within the waypoint server"}), status.HTTP_202_ACCEPTED
            )
        agv.delete()
        return make_response(jsonify({"message": "AGV successfully deleted"}), status.HTTP_200_OK)


agvs_api.add_resource(AGVCreateView, "/")
agvs_api.add_resource(AGVDetailView, "/<int:id>/")
agvs_api.add_resource(AGVListView, "/agvs/")
