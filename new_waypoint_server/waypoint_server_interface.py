import json

import requests

IP = "192.168.0.100"  # IP of the machine the Waypoint Server is hosted off of
PORT = "5000"  # PORT from which the Waypoint Server is hosted off of
DEBUG = True  # Controls whether Waypoint Server response JSON is printed


def test_waypoint_server_connection():
    response = requests.get(f"http://{IP}:{PORT}/agv_request_handlers/test_connection/")
    if DEBUG:
        print(response.status_code, response.json())


def create_agv(id, x=0, y=0, theta=0, status="READY"):
    agv_data = {
        "id": id,
        "x": x,
        "y": y,
        "theta": theta,
        "status": "status",
    }
    response = requests.post(f"http://{IP}:{PORT}/agvs/", data=agv_data)
    if DEBUG:
        print(response.status_code, response.json())


def list_agvs():
    response = requests.get(f"http://{IP}:{PORT}/agvs/agvs/")
    if DEBUG:
        print(response.status_code, response.json())


def get_agv(id):
    response = requests.get(f"http://{IP}:{PORT}/agvs/{id}/")
    if DEBUG:
        print(response.status_code, response.json())


def delete_agv(id):
    response = requests.delete(f"http:/{IP}:{PORT}/agvs/{id}/")
    if DEBUG:
        print(response.status_code, response.json())


def delete_all_agvs():
    response = requests.delete(f"http://{IP}:{PORT}/agvs/agvs/")
    if DEBUG:
        print(response.status_code, response.json())


def create_task(task_json):
    """
    task_json should be in the format shown below

    task_json = {
        priority:String (of the PriorityType Enum) - OPTIONAL
        drive_train_type:String (of the AGVDriveTrainType Enum) - OPTIONAL
        agv_id:Integer - OPTIONAL
        waypoints: [
            {
                x:Float,
                y:Float,
                theta:Float,
                order:Integer
            },
            ...
        ]
    }
    """
    response = requests.post(f"http://{IP}:{PORT}/tasks/", json=task_json)
    if DEBUG:
        print(response.status_code, response.json())


def list_tasks(status=None, priority=None):
    query_params = {
        "status": status,
        "priority": priority,
    }
    if any(query_params.values()):
        response = requests.get(f"http://{IP}:{PORT}/tasks/tasks/", params=query_params)
    else:
        response = requests.get(f"http://{IP}:{PORT}/tasks/tasks/")
    if DEBUG:
        print(response.status_code, response.json())


def get_task(id):
    response = requests.get(f"http://{IP}:{PORT}/tasks/{id}/")
    if DEBUG:
        print(response.status_code, response.json())


def delete_task(id):
    response = requests.delete(f"http://{IP}:{PORT}/tasks/{id}/")
    if DEBUG:
        print(response.status_code, response.json())


def delete_all_tasks():
    response = requests.delete(f"http://{IP}:{PORT}/tasks/tasks/")
    if DEBUG:
        print(response.status_code, response.json())


def create_command(command_json):
    """
    command_json should be in the format shown below,
    NOTE: the inclusion of either agv_id or task_id is required

    command_json = {
        "agv_id":Integer,
        "task_id":Integer,
        "type":String (of the CommandType Enum)
    }
    """
    response = requests.post(f"http://{IP}:{PORT}/commands/", data=command_json)
    if DEBUG:
        print(response.status_code, response.json())


def list_commands(agv_id=None, task_id=None, type=None, processed=None):
    query_params = {
        "agv_id": None,
        "task_id": None,
        "type": None,
        "processed": None,
    }
    if any(query_params.values()):
        response = requests.get(f"http://{IP}:{PORT}/commands/commands/", params=query_params)
    else:
        response = requests.get(f"http://{IP}:{PORT}/commands/commands/")
    if DEBUG:
        print(response.status_code, response.json())


def get_command(id):
    response = requests.get(f"http://{IP}:{PORT}/commands/{id}/")
    if DEBUG:
        print(response.status_code, response.json())


def delete_command(id):
    response = requests.delete(f"http://{IP}:{PORT}/commands/{id}/")
    if DEBUG:
        print(response.status_code, response.json())


def delete_all_commands():
    response = requests.delete(f"http://{IP}:{PORT}/commands/commands/")
    if DEBUG:
        print(response.status_code, response.json())
