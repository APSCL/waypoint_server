import sys

from app.app import create_app
from app.config import ConfigType
from app.database import db
from app.tasks.constants import Priority, TaskStatus
from app.tests.utils import create_task, create_waypoint
from flask_api import status
from flask_testing import TestCase


class TestAGVCrud(TestCase):
    base_url = "tasks/"

    def create_app(self):
        return create_app(ConfigType.TESTING)

    def setUp(self):
        db.create_all()

    def test_create_task_successful(self):
        # mocking how registration would work for AGVs
        payload = {
            "priority": str(Priority.HIGH),
            "status": str(TaskStatus.INCOMPLETE),
            "waypoints": [{"x": 1, "y": 1, "order": 1}],
        }
        response = self.client.post(f"{self.base_url}", json=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected_response = {
            "num_waypoints": 1,
            "priority": str(Priority.HIGH),
            "status": str(TaskStatus.INCOMPLETE),
        }
        response_data = response.get_json()
        for key in expected_response.keys():
            self.assertEqual(response_data[key], expected_response[key])

    def test_task_creation_validation(self):
        # Test Task creation fails when you provide it an empty task!
        payload = {
            "priority": str(Priority.HIGH),
            "status": str(TaskStatus.INCOMPLETE),
        }
        response = self.client.post(f"{self.base_url}", json=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.get_json()["error"],
            "No valid waypoints provided",
        )

        # Test Task creation fails when you provide a waypoint with coordinates that are out of bounds
        payload["waypoints"] = [{"x": sys.maxsize, "y": sys.maxsize, "order": 1}]
        response = self.client.post(f"{self.base_url}", json=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.get_json()["error"]["_schema"][0],
            "X or Y coordinate is out of bounds for the allowable range of navigatable coordinates",
        )

        # Test that task creation fails when you provide waypoints with a repetitive "order" value
        payload["waypoints"] = [{"x": 0, "y": 0, "order": 1}, {"x": 0, "y": 0, "order": 1}]
        response = self.client.post(f"{self.base_url}", json=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.get_json()["error"], "Ordering of waypoints provided invalid - repetition in order detected"
        )

    def test_retrieve_single_task(self):
        # Test that our request is rejected for requesting a task that doesn't exist
        waypoint_params = {"x": 1, "y": 1, "order": 1}
        waypoint = create_waypoint(**waypoint_params)
        task_params = {
            "priority": Priority.HIGH,
            "status": TaskStatus.INCOMPLETE,
            "waypoints": [waypoint],
        }
        task = create_task(**task_params)
        bad_id = 1000
        response = self.client.get(f"{self.base_url}{bad_id}/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_data = response.get_json()
        self.assertEqual(response_data["message"], f"Task does not exist within the waypoint server")

        # Test that our request to retrieve a singular task is accepted under the right conditions
        response = self.client.get(f"{self.base_url}{task.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.get_json()
        response_data.pop("waypoints"), task_params.pop("waypoints")
        for key in task_params.keys():
            self.assertEqual(str(response_data[key]), str(task_params[key]))

    def test_delete_single_task(self):
        # Test that our request is rejected for attempting to delete a task that doesn't exist
        waypoint_params = {"x": 1, "y": 1, "order": 1}
        waypoint = create_waypoint(**waypoint_params)
        task_params = {
            "priority": Priority.HIGH,
            "status": TaskStatus.INCOMPLETE,
            "waypoints": [waypoint],
        }
        task = create_task(**task_params)
        bad_id = 1000
        response = self.client.delete(f"{self.base_url}{bad_id}/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_data = response.get_json()
        self.assertEqual(response_data["message"], f"Task does not exist within the waypoint server")

        # Test that our request to delete a singular task is accepted under the right conditions
        response = self.client.delete(f"{self.base_url}{task.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_tasks(self):
        task_params_list = [
            {
                "priority": Priority.LOW,
                "status": TaskStatus.INCOMPLETE,
            },
            {
                "priority": Priority.MEDIUM,
                "status": TaskStatus.COMPLETE,
            },
        ]
        [create_task(**task_params) for task_params in task_params_list]
        response = self.client.get(f"{self.base_url}tasks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.get_json()
        self.assertEqual(type(response_data), list)
        for param_tuple in zip(response_data, task_params_list):
            keys = param_tuple[1].keys()
            response_task, reference_task = param_tuple
            for key in keys:
                self.assertEqual(response_task[key], str(reference_task[key]))

        filter_params = {"priority": "MEDIUM", "status": "COMPLETE"}
        response = self.client.get(f"{self.base_url}tasks/", query_string=filter_params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.get_json()
        self.assertEqual(type(response_data), list)
        keys = task_params_list[1].keys()
        response_task, reference_task = response_data[0], task_params_list[1]
        for key in keys:
            self.assertEqual(response_task[key], str(reference_task[key]))

    def test_delete_all_tasks(self):
        # First test that a delete request with no existing tasks is rejected
        response = self.client.delete(f"{self.base_url}tasks/")
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        response_data = response.get_json()
        self.assertEqual(response_data["message"], "No Tasks currently exist to delete")

        # Test that deleting all tasks works successfully
        [create_task() for i in range(3)]
        response = self.client.delete(f"{self.base_url}tasks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.get_json()
        self.assertEqual(response_data["message"], "All Tasks successfully deleted")

        response = self.client.get(f"{self.base_url}tasks/")
        response_data = response.get_json()
        self.assertEqual(response_data, [])

    def tearDown(self):
        db.session.remove()
        db.drop_all()
