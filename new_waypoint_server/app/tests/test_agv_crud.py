import sys

from app.agvs.constants import AGVState
from app.app import create_app
from app.config import ConfigType
from app.database import db
from app.tests.utils import create_agv
from flask_api import status
from flask_testing import TestCase


class TestAGVCrud(TestCase):
    base_url = "agvs/"

    def create_app(self):
        return create_app(ConfigType.TESTING)

    def setUp(self):
        db.create_all()

    def test_create_agv_successful(self):
        payload = {
            "id": 1,
            "x": 1.0,
            "y": 1.0,
            "theta": 3.14,
            "status": str(AGVState.READY),
        }
        response = self.client.post(f"{self.base_url}", data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = response.get_json()
        for key in payload.keys():
            self.assertEqual(response_data[key], payload[key])

    def test_create_agv_validation(self):
        payload = {
            "id": 1,
            "x": sys.maxsize,
            "y": sys.maxsize,
            "theta": 3.14,
            "status": str(AGVState.READY),
        }

        response = self.client.post(f"{self.base_url}", data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.get_json()["_schema"][0], "X or Y coordinate is out of the allowable range of coordinates"
        )

        payload["x"] = 0
        payload["y"] = 0
        payload["theta"] = sys.maxsize
        response = self.client.post(f"{self.base_url}", data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.get_json()["_schema"][0], "theta is out of bounds from the allowable range of values: [-pi, pi]"
        )

        payload["theta"] = 0
        response = self.client.post(f"{self.base_url}", data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # test that agv cannot be created with the same id
        response = self.client.post(f"{self.base_url}", data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.get_json()["_schema"][0], "AGV with provided ROS_DOMAIN_ID already registered!")

    def test_retrieve_single_task(self):
        agv_params = {
            "id": 1,
            "x": 1.0,
            "y": 1.0,
            "theta": 3.14,
            "status": str(AGVState.READY),
        }
        agv = create_agv(**agv_params)
        bad_id = 1000
        response = self.client.get(f"{self.base_url}{bad_id}/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_data = response.get_json()
        self.assertEqual(
            response_data["message"], f"AGV with ROS_DOMAIN_ID is not registered within the waypoint server"
        )

        response = self.client.get(f"{self.base_url}{agv.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.get_json()
        for key in agv_params.keys():
            self.assertEqual(str(response_data[key]), str(agv_params[key]))

    def test_delete_single_task(self):
        agv_params = {
            "id": 1,
            "x": 1.0,
            "y": 1.0,
            "theta": 3.14,
            "status": str(AGVState.READY),
        }
        agv = create_agv(**agv_params)
        bad_id = 1000
        response = self.client.delete(f"{self.base_url}{bad_id}/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_data = response.get_json()
        self.assertEqual(
            response_data["message"], f"AGV with ROS_DOMAIN_ID is not registered within the waypoint server"
        )

        response = self.client.delete(f"{self.base_url}{agv.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_agvs(self):
        agv_params_list = [
            {
                "id": 1,
                "x": 0.0,
                "y": 0.0,
                "theta": 0.0,
                "status": AGVState.READY,
            },
            {
                "id": 2,
                "x": 0.0,
                "y": 0.0,
                "theta": 0.0,
                "status": AGVState.BUSY,
            },
        ]
        [create_agv(**agv_params) for agv_params in agv_params_list]
        response = self.client.get(f"{self.base_url}agvs/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.get_json()
        self.assertEqual(type(response_data), list)
        for param_tuple in zip(response_data, agv_params_list):
            keys = param_tuple[1].keys()
            response_agv, reference_agv = param_tuple
            for key in keys:
                self.assertEqual(str(response_agv[key]), str(reference_agv[key]))

        filter_params = {"status": "READY"}
        response = self.client.get(f"{self.base_url}agvs/", query_string=filter_params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.get_json()
        self.assertEqual(type(response_data), list)
        keys = agv_params_list[0].keys()
        response_agv, reference_agv = response_data[0], agv_params_list[0]
        for key in keys:
            self.assertEqual(str(response_agv[key]), str(reference_agv[key]))

    def test_delete_all_agvs(self):
        response = self.client.delete(f"{self.base_url}agvs/")
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        response_data = response.get_json()
        self.assertEqual(response_data["message"], "No AGVs currently exist to delete")

        [create_agv() for i in range(3)]
        response = self.client.delete(f"{self.base_url}agvs/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.get_json()
        self.assertEqual(response_data["message"], "All AGVs successfully deleted")

        response = self.client.get(f"{self.base_url}agvs/")
        response_data = response.get_json()
        self.assertEqual(response_data, [])

    def tearDown(self):
        db.session.remove()
        db.drop_all()
