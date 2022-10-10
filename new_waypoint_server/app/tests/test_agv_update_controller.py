from unittest.mock import patch

from app.agv_request_handlers.controllers import AGVUpdateController
from app.agvs.constants import AGVState
from app.app import create_app
from app.config import ConfigType
from app.database import db
from app.tasks.constants import TaskStatus
from app.tasks.models import Waypoint
from app.tests.utils import create_agv, create_task, create_waypoint
from flask_testing import TestCase


class TestAGVUpdateController(TestCase):
    def create_app(self):
        return create_app(ConfigType.TESTING)

    def setUp(self):
        db.create_all()

    def test_update_agv_ready(self):
        agv = create_agv(status=AGVState.READY)
        data = {
            "id": agv.id,
            "status": AGVState.READY,
            "x": 0.5,
            "y": 1.5,
            "theta": 1.5,
        }
        with patch("app.agv_request_handlers.controllers.CommandProcessingController") as mock:
            mock.get_next_command.return_value = None
            result = AGVUpdateController.update_agv(data)
            expected_output = (True, None, None)
            self.assertEqual(result, expected_output)

        attrs = ["status", "x", "y", "theta", "id"]
        for attr in attrs:
            self.assertEqual(data.get(attr, None), getattr(agv, attr))

    def test_update_agv_busy(self):
        agv = create_agv(status=AGVState.BUSY)
        waypoints = [create_waypoint(order=order) for order in [1, 2]]
        task = create_task(status=TaskStatus.IN_PROGRESS, agv_id=agv.id, waypoints=waypoints)
        data = {
            "id": agv.id,
            "status": AGVState.BUSY,
            "x": 0.5,
            "y": 1.5,
            "theta": 1.5,
            "current_task_id": task.id,
            "current_waypoint_order": 2,
        }

        with patch("app.agv_request_handlers.controllers.CommandProcessingController") as mock:
            mock.get_next_command.return_value = None
            result = AGVUpdateController.update_agv(data)
            expected_output = (True, None, None)
            self.assertEqual(result, expected_output)

        agv_attrs = ["status", "x", "y", "theta", "id"]
        for attr in agv_attrs:
            self.assertEqual(data.get(attr, None), getattr(agv, attr))

        # validate that busy update behavior successfully updates visited waypoints
        waypoint = Waypoint.query.filter_by(task_id=task.id, order=1).first()
        self.assertEqual(waypoint.visited, True)

        waypoint = Waypoint.query.filter_by(task_id=task.id, order=2).first()
        self.assertEqual(waypoint.visited, False)

    def test_update_agv_done(self):
        agv = create_agv(status=AGVState.DONE)
        waypoints = [create_waypoint(order=order) for order in [1, 2]]
        task = create_task(status=TaskStatus.IN_PROGRESS, agv_id=agv.id, waypoints=waypoints)
        data = {
            "id": agv.id,
            "status": AGVState.DONE,
            "x": 0.5,
            "y": 1.5,
            "theta": 1.5,
            "current_task_id": task.id,
        }

        with patch("app.agv_request_handlers.controllers.CommandProcessingController") as mock:
            mock.get_next_command.return_value = None
            result = AGVUpdateController.update_agv(data)
            expected_output = (True, None, None)
            self.assertEqual(result, expected_output)

        agv_attrs = ["status", "x", "y", "theta", "id"]
        for attr in agv_attrs:
            self.assertEqual(data.get(attr, None), getattr(agv, attr))

        # assert that the task has been marked as complete, and its associated waypoints as well
        self.assertEqual(task.status, TaskStatus.COMPLETE)
        for waypoint in task.waypoints:
            self.assertEqual(waypoint.visited, True)

        # assert that the AGV no longer has a task registed
        self.assertEqual(agv.current_task_id, None)

    def test_update_agv_stopped(self):
        agv = create_agv(status=AGVState.STOPPED)
        data = {
            "id": agv.id,
            "status": AGVState.STOPPED,
            "x": 0.5,
            "y": 1.5,
            "theta": 1.5,
        }
        with patch("app.agv_request_handlers.controllers.CommandProcessingController") as mock:
            mock.get_next_command.return_value = None
            result = AGVUpdateController.update_agv(data)
            expected_output = (True, None, None)
            self.assertEqual(result, expected_output)

        agv_attrs = ["status", "x", "y", "theta", "id"]
        for attr in agv_attrs:
            self.assertEqual(data.get(attr, None), getattr(agv, attr))

    def tearDown(self):
        db.session.remove()
        db.drop_all()
