import sys
from unittest.mock import patch

from app.agvs.constants import AGVState
from app.app import create_app
from app.config import ConfigType
from app.database import db
from app.tests.utils import create_agv
from flask_api import status
from flask_testing import TestCase


class TestAGVHandlers(TestCase):
    base_url = "agv_request_handlers/"

    def create_app(self):
        return create_app(ConfigType.TESTING)

    def test_ping_waypoint_server_success(self):
        response = self.client.get(f"{self.base_url}test_connection/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_request_task_success(self):
        agv = create_agv(status=AGVState.READY)
        data = {
            "id": agv.id,
            "status": str(AGVState.READY),
            "x": agv.x,
            "y": agv.y,
            "theta": agv.theta,
        }
        with patch("app.agv_request_handlers.views.TaskAssignmentController") as mock:
            mock_status_code, mock_task_data = 200, {"message": "yeet"}
            mock.get_task_for_agv.return_value = mock_status_code, mock_task_data
            response = self.client.get(f"{self.base_url}request_task/", json=data)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            mock.get_task_for_agv.assert_called_once()

    def test_request_task_validation(self):
        agv = create_agv(status=AGVState.READY)
        data = {
            "id": -1,
            "status": str(AGVState.READY),
            "x": agv.x,
            "y": agv.y,
            "theta": agv.theta,
        }

        # Test that only AGVs that are registered inside the database can be assigned tasks
        response = self.client.get(f"{self.base_url}request_task/", json=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.get_json()
        self.assertEqual(
            response_data["_schema"][0], "AGV with provided ROS_DOMAIN_ID is not registered!"
        )

        data["id"] = agv.id
        data["x"] = sys.maxsize

        response = self.client.get(f"{self.base_url}request_task/", json=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.get_json()
        self.assertEqual(
            response_data["_schema"][0],
            "X or Y coordinate is out of bounds for the allowable range of navigatable coordinates",
        )

        data["x"] = agv.x
        data["theta"] = sys.maxsize

        response = self.client.get(f"{self.base_url}request_task/", json=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.get_json()
        self.assertEqual(
            response_data["_schema"][0],
            "theta is out of bounds from the allowable range of values: [-pi, pi]",
        )

        data["theta"] = agv.theta
        data["status"] = str(AGVState.BUSY)

        response = self.client.get(f"{self.base_url}request_task/", json=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.get_json()
        self.assertEqual(response_data["_schema"][0], "Invalid data for AGV:READY Update")

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
