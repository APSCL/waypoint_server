from app.agvs.constants import AGVState
from app.app import create_app
from app.commands.constants import CommandTypes
from app.config import ConfigType
from app.database import db
from app.tasks.constants import TaskStatus
from app.tests.utils import create_agv, create_command, create_task
from flask_api import status
from flask_testing import TestCase


class TestCommandCrud(TestCase):
    base_url = "commands/"

    def create_app(self):
        return create_app(ConfigType.TESTING)

    def setUp(self):
        db.create_all()

    def test_create_command_successful(self):
        # Test the sucessful creation of AGV Commands
        agv = create_agv()
        payload = {
            "agv_id": agv.id,
            "type": "STOP_AGV",
        }
        response = self.client.post(f"{self.base_url}", data=payload)
        # Assert that the creation request returned with the appropriate http response: 201
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = response.get_json()

        # Assert that the response data returned mathces our expectations (json for the command created)
        payload["task_id"] = None
        for key in payload.keys():
            self.assertEqual(response_data[key], payload[key])

        # Test the sucessful creation of Task Commands
        task = create_task(status=TaskStatus.IN_PROGRESS)
        payload = {
            "task_id": task.id,
            "type": "CANCEL_TASK",
        }
        response = self.client.post(f"{self.base_url}", data=payload)
        # Assert that the creation request returned with the appropriate http response: 201
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = response.get_json()

        # Assert that the response data returned mathces our expectations (json for the command created)
        payload["agv_id"] = None
        for key in payload.keys():
            self.assertEqual(response_data[key], payload[key])

    def test_create_command_general_validation(self):
        # Test that command must have at least a task_id or agv_id defined
        payload = {
            "type": "STOP_AGV",
        }
        response = self.client.post(f"{self.base_url}", data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_data = response.get_json()
        self.assertEqual(response_data["_schema"][0], "Command provided without and AGV or Task ID")

        # Test that command rejects creation upon providing both an agv_id and a task_id
        payload = {
            "agv_id": 1,
            "task_id": 1,
            "type": "STOP_AGV",
        }
        response = self.client.post(f"{self.base_url}", data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_data = response.get_json()
        self.assertEqual(response_data["_schema"][0], "Command cannot be created with both a AGV a Task ID")

        # Test that command rejects creation upon providing an agv related command without an agv id
        payload = {
            "task_id": 1,
            "type": "STOP_AGV",
        }
        response = self.client.post(f"{self.base_url}", data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_data = response.get_json()
        self.assertEqual(response_data["_schema"][0], "AGV Command Type provided with no valid AGV ID")

        # Test that command rejects creation upon providing a task related command without a task id
        payload = {
            "agv_id": 1,
            "type": "CANCEL_TASK",
        }
        response = self.client.post(f"{self.base_url}", data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_data = response.get_json()
        self.assertEqual(response_data["_schema"][0], "Task Command Type provided with no valid Task ID")

        # Test that command creation rejects for agv related commands without an AGV matching the agv_id provided
        agv = create_agv()
        payload = {
            "agv_id": -1,
            "type": "CANCEL_AGV",
        }
        response = self.client.post(f"{self.base_url}", data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_data = response.get_json()
        self.assertEqual(response_data["_schema"][0], "AGV with provided id not found!")

        # Test that command creation rejects for Task related commands without an Task matching the task_id provided
        agv = create_task()
        payload = {
            "task_id": -1,
            "type": "CANCEL_TASK",
        }
        response = self.client.post(f"{self.base_url}", data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_data = response.get_json()
        self.assertEqual(response_data["_schema"][0], "Task with provided id not found!")

        # Test that commands besides START_AGV cannot be provided when an AGV is STOPPED (AGVState)
        agv_stopped = create_agv(status=AGVState.STOPPED)
        payload = {
            "agv_id": agv_stopped.id,
            "type": "CANCEL_AGV",
        }
        response = self.client.post(f"{self.base_url}", data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_data = response.get_json()
        self.assertEqual(
            response_data["_schema"][0], "AGV cannot accept new commands (except for START_AGV) while it is stopped!"
        )

    def test_start_agv_command_validation(self):
        # Test that a START_AGV command cannot be created if the AGV is not currently STOPPED
        agv = create_agv(status=AGVState.BUSY)
        payload = {
            "agv_id": agv.id,
            "type": "START_AGV",
        }
        response = self.client.post(f"{self.base_url}", data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_data = response.get_json()
        self.assertEqual(response_data["_schema"][0], "Invalid creation for command: START_AGV")

        # Test that a START_AGV command cannot be created if one already exists
        agv.update(status=AGVState.STOPPED)
        prexisting_start_agv_command = create_command(agv_id=agv.id, type=CommandTypes.START_AGV)
        response = self.client.post(f"{self.base_url}", data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_data = response.get_json()
        self.assertEqual(response_data["_schema"][0], "Invalid creation for command: START_AGV")

    def test_stop_agv_command_validation(self):
        # Test that a STOP_AGV command cannot be created if one already exists
        agv = create_agv(status=AGVState.BUSY)
        payload = {
            "agv_id": agv.id,
            "type": "STOP_AGV",
        }
        prexisting_start_agv_command = create_command(agv_id=agv.id, type=CommandTypes.STOP_AGV)
        response = self.client.post(f"{self.base_url}", data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_data = response.get_json()
        self.assertEqual(response_data["_schema"][0], "Invalid creation for command: STOP_AGV")

    def test_cancel_agv_command_validation(self):
        # Test that a CANCEL_AGV command cannot be created if the AGV is not BUSY
        agv = create_agv(status=AGVState.READY)
        payload = {
            "agv_id": agv.id,
            "type": "CANCEL_AGV",
        }
        response = self.client.post(f"{self.base_url}", data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_data = response.get_json()
        self.assertEqual(response_data["_schema"][0], "Invalid creation for command: CANCEL_AGV")

    def test_cancel_task_command_validation(self):
        # Test that a CANCEL_AGV command cannot be created if the Task is not IN_PROGRESS
        task = create_task(status=TaskStatus.INCOMPLETE)
        payload = {
            "task_id": task.id,
            "type": "CANCEL_TASK",
        }
        response = self.client.post(f"{self.base_url}", data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_data = response.get_json()
        self.assertEqual(response_data["_schema"][0], "Invalid creation for command: CANCEL_TASK")

    def test_list_commands(self):
        # Test that we can successfully retrieve a list of all existing commands
        agv = create_agv()
        task = create_task()
        command_params = [{"agv_id": agv.id, "type": "STOP_AGV"}, {"task_id": task.id, "type": "CANCEL_TASK"}]
        [create_command(**params) for params in command_params]

        response = self.client.get(f"{self.base_url}commands/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.get_json()
        self.assertEqual(type(response_data), list)
        for param_tuple in zip(response_data, command_params):
            keys = param_tuple[1].keys()
            response_command, reference_command = param_tuple
            for key in keys:
                self.assertEqual(response_command[key], reference_command[key])

        # Test that we can successfully retrieve a list of filtered commands
        filter_params = {"type": "STOP_AGV", "agv_id": agv.id}
        response = self.client.get(f"{self.base_url}commands/", query_string=filter_params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.get_json()
        self.assertEqual(type(response_data), list)
        keys = command_params[0].keys()
        response_command, reference_command = response_data[0], command_params[0]
        for key in keys:
            self.assertEqual(response_command[key], reference_command[key])

    def test_delete_all_commands(self):
        # First test that a delete request with no existing commands is rejected
        response = self.client.delete(f"{self.base_url}commands/")
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        response_data = response.get_json()
        self.assertEqual(response_data["message"], "No Commands currently exist to delete")

        # Test that deleting all commands works successfully
        [create_command() for i in range(3)]
        response = self.client.delete(f"{self.base_url}commands/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.get_json()
        self.assertEqual(response_data["message"], "All Commands successfully deleted")

        response = self.client.get(f"{self.base_url}commands/")
        response_data = response.get_json()
        self.assertEqual(response_data, [])

    def test_retrieve_single_command(self):
        # Test that our request is rejected for requesting a command that doesn't exist
        command_params = {"type": CommandTypes.STOP_AGV, "agv_id": 1}
        command = create_command(**command_params)
        bad_id = 1000
        response = self.client.get(f"{self.base_url}{bad_id}/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_data = response.get_json()
        self.assertEqual(
            response_data["message"], f"Command with ID={bad_id} is not registered within the waypoint server"
        )

        # Test that our request to retrieve a singular command is accepted under the right conditions
        response = self.client.get(f"{self.base_url}{command.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.get_json()
        for key in command_params.keys():
            self.assertEqual(str(response_data[key]), str(command_params[key]))

    def test_delete_single_command(self):
        # Test that our request is rejected for attempting to delete a command that doesn't exist
        command_params = {"type": CommandTypes.STOP_AGV, "agv_id": 1}
        command = create_command(**command_params)
        bad_id = 1000
        response = self.client.delete(f"{self.base_url}{bad_id}/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response_data = response.get_json()
        self.assertEqual(response_data["message"], f"Command was not registered within the waypoint server")

        # Test that our request to delete a singular command is accepted under the right conditions
        response = self.client.delete(f"{self.base_url}{command.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
