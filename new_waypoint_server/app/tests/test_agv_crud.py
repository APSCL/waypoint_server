from app.agvs.constants import AGVState
from app.agvs.models import AGV
from app.app import create_app
from app.config import ConfigType
from app.database import db
from app.tasks.models import Task, Waypoint
from app.tests.utils import create_agv, create_task
from flask_api import status
from flask_testing import TestCase


# Example Test Case for future use
class TestAGVCrud(TestCase):
    base_url = "agvs/"

    def create_app(self):
        return create_app(ConfigType.TESTING)

    def setUp(self):
        db.create_all()

    def test_create_agv_successful(self):
        # mocking how registration would work for AGVs
        payload = {
            "id": 1, 
            "x": 1.0,
            "y": 1.0,
            "theta": 3.14,
            "status": str(AGVState.READY),
        }
        response = self.client.post(f"{self.base_url}", data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # TODO: verify that creation was successful!

    def test_update_agv(self):
        # mocking how updates would work for AGVs
        payload = {
            "x": 1.0,
            "y": 1.0,
            "theta": 3.14,
            "status": str(AGVState.READY),
            "current_task_id": 1,
            "current_waypoint_id": 2,
        }

    def test_get_agvs(self):
        pass

    def tearDown(self):
        db.session.remove()
        db.drop_all()
