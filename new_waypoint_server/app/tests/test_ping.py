from app.app import create_app
from app.config import ConfigType
from app.database import db
from flask_api import status
from flask_testing import TestCase


# Example Test Case for future use
class TestServerPing(TestCase):
    def create_app(self):
        return create_app(ConfigType.TESTING)

    def setUp(self):
        db.create_all()

    def test_ping(self):
        response = self.client.get("/agv_request_handlers/test_connection/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
