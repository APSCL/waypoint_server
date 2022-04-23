from flask_testing import TestCase
from app.config import ConfigType
from app import create_app, db

class BaseTestCase(TestCase):
    def create_app(self):
        return create_app(ConfigType.TESTING)

    def setUp(self):
        db.create_all()

    def test_ping(self):
        response = self.client.get("/pings/test_connection")
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        db.session.remove()
        db.drop_all()