import sys

from app.agvs.constants import AGVState
from app.agvs.models import AGV
from app.core.constants import PoseAssigners
from app.core.coord_standardization_config import HARD_CODED_AGV_INITAL_POSE
from flask import current_app


# NOTE: Currently the Pose Assignment Controller is not being used within our system. For future teams,
# consider using the framework below to implement (one of many potential methods) coordinate standardization
class PoseAssignmentController:
    @classmethod
    def perform_pose_assignment(cls, agv):
        pose_assigner_key = current_app.config["POSE_ASSIGMENT_METHOD"]
        pose_assignment_map = {
            PoseAssigners.HARDCODED: cls.hardcoded_pose_assigment,
        }
        method = pose_assignment_map.get(pose_assigner_key, None)
        if method is None:
            # No pose assigner set, thus, don't do anything to the initial pose of the AGV
            return
        method(agv)

    @classmethod
    def hardcoded_pose_assigment(cls, agv):
        available_assignment_agv_ids = list(HARD_CODED_AGV_INITAL_POSE.keys())
        print(available_assignment_agv_ids)
        if agv.id not in available_assignment_agv_ids:
            # We don't have an assigned hardcode mapping - do nothing
            return
        agv_assigned_x, agv_assigned_y = HARD_CODED_AGV_INITAL_POSE.get(agv.id)
        agv.x, agv.y = agv_assigned_x, agv_assigned_y
        agv.save()
