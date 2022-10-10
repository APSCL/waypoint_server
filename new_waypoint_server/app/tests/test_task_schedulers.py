from app.agvs.constants import AGVState
from app.app import create_app
from app.config import ConfigType
from app.database import db
from app.task_scheduler.scheduler import GreedyTaskSchedulerSJF
from app.tasks.constants import Priority
from app.tests.utils import create_agv, create_task, create_waypoint
from flask_testing import TestCase


class TestCommandProcessingController(TestCase):
    def create_app(self):
        return create_app(ConfigType.TESTING)

    def test_greedy_path_task_scheduler(self):
        agv = create_agv(status=AGVState.BUSY, x=0, y=0)
        waypoint_data_1 = {"x": 1, "y": 1, "order": 1}
        waypoint_data_2 = {"x": 2, "y": 2, "order": 2}
        waypoint_data_3 = {"x": 3, "y": 3, "order": 3}
        longer_task_waypoints = [waypoint_data_1, waypoint_data_2, waypoint_data_3]
        medium_task_waypoints = [waypoint_data_1, waypoint_data_2]
        shorter_task_waypoints = [waypoint_data_1]
        high_priority_long_task = create_task(
            priority=Priority.HIGH,
            waypoints=[create_waypoint(**kwargs) for kwargs in longer_task_waypoints],
        )
        high_priority_medium_task = create_task(
            priority=Priority.HIGH,
            waypoints=[create_waypoint(**kwargs) for kwargs in medium_task_waypoints],
        )
        low_priority_short_task = create_task(
            priority=Priority.LOW,
            waypoints=[create_waypoint(**kwargs) for kwargs in shorter_task_waypoints],
        )
        tasks = [high_priority_long_task, high_priority_medium_task, low_priority_short_task]
        optimal_task = GreedyTaskSchedulerSJF.generate_optimal_assignment(agv, tasks)
        self.assertEqual(optimal_task.id, high_priority_medium_task.id)

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
