from ipaddress import ip_address

from app.agvs.constants import AGVState
from app.agvs.models import AGV
from app.app import create_app
from app.config import ConfigType
from app.database import db
from app.tasks.constants import Priority, TaskStatus
from app.tasks.models import Task, Waypoint
from flask_api import status
from flask_testing import TestCase


# Example Test Case for future use
class TestCreateWaypointModels(TestCase):
    def create_app(self):
        return create_app(ConfigType.TESTING)

    def setUp(self):
        db.create_all()

    # def test_create_agv(self):
    #     ip, x, y = "1.0.0.2", 0.1, 0.2
    #     status = AGVState.BUSY
    #     agv = AGV(ip_address=ip, position_x=x, position_y=y, status=status)
    #     db.session.add(agv)
    #     db.session.commit()
    #     # print(agv)
    #     # TODO: make assert equal stuff

    # def test_create_task(self):
    #     task_status, priority = TaskStatus.COMPLETE, Priority.HIGH
    #     task = Task(priority=priority, status=task_status)
    #     db.session.add(task)
    #     db.session.commit()
    #     # print(task)
    #     # TODO: make assert equal stuff

    # def test_create_waypoint(self):
    #     x, y = 0.1, 0.2
    #     waypoint = Waypoint(position_x=x, position_y=y)
    #     db.session.add(waypoint)
    #     db.session.commit()
    #     # print(waypoint)
    #     # TODO: make assert equal stuff

    # def test_create_task_with_waypoints_and_assign_agv(self):
    #     x1,x2,x3 = 0.1, 0.2, 0.3
    #     y1,y2,y3 = 0.1, 0.2, 0.3
    #     waypoint1 = Waypoint(position_x=x1, position_y=y1)
    #     waypoint2 = Waypoint(position_x=x2, position_y=y2)
    #     waypoint3 = Waypoint(position_x=x3, position_y=y3)
    #     waypoint1.next_waypoint = waypoint2
    #     waypoint2.next_waypoint = waypoint3
    #     db.session.add(waypoint1)
    #     db.session.add(waypoint2)
    #     db.session.add(waypoint3)
    #     db.session.commit()

    #     task_status, priority = TaskStatus.INCOMPLETE, Priority.MEDIUM
    #     task = Task(starting_waypoint_id=waypoint1.id, priority=priority, status=task_status)

    #     task.waypoints.append(waypoint1)
    #     task.waypoints.append(waypoint2)
    #     task.waypoints.append(waypoint3)
    #     db.session.add(task)
    #     db.session.commit()

    #     status = AGVState.READY
    #     agv = AGV(status=status)

    #     agv.task = task

    #     db.session.add(agv)
    #     db.session.commit()
    # print(agv)
    # print(task)
    # print(waypoint1)
    # print(waypoint2)
    # print(waypoint3)
    # print(task.waypoints)
    # print(waypoint1.task)
    # print(waypoint1.next_waypoint)
    # print(task.starting_waypoint_id)
    # print(task.path_dist_lower_bound)
    # print(task.num_waypoints)
    # TODO: make assert equal stuff

    def tearDown(self):
        db.session.remove()
        db.drop_all()
