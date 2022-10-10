from functools import cached_property

from app.agvs.constants import AGVDriveTrainType
from app.core.utils import euclidean_dist
from app.database import Column, Model, db, relationship

from .constants import Priority, TaskStatus


# TODO: Add an internal ordering field when this task is registered to an AGV
class Task(Model):
    """
    This model servers as the internal representation for user created tasks

    id : A unique identifier for each Task
    priority : the user specified urgency of a task (can be LOW, MEDIUM, HIGH), priority is taken into acount by the scheduling algorithms
    status : indicates which stage of processing a Task is in (ie - INCOMPLETE, IN_PROGRESS, COMPLETE)
    drive_train_type : indicates the Task is reserved for an AGV with a specific drive train (can be MECANUM, ACKERMANN)
    waypoints : relational link to the waypoints (locations on a 2D plane) associated with this task
    agv_id : indicates which AGV this task is assigned to
    """

    __tablename__ = "task"
    id = Column(db.Integer, primary_key=True)
    priority = Column(db.Enum(Priority), default=Priority.MEDIUM, nullable=False)
    status = Column(db.Enum(TaskStatus), default=TaskStatus.INCOMPLETE, nullable=False)
    drive_train_type = Column(db.Enum(AGVDriveTrainType), default=None, nullable=True)
    waypoints = relationship(
        "Waypoint",
        backref="task",
    )
    agv_id = Column(db.Integer, db.ForeignKey("agv.id"))

    @cached_property
    def num_waypoints(self):
        if not self.waypoints:
            return 0
        return len(self.waypoints)

    @cached_property
    def starting_waypoint(self):
        return Waypoint.query.filter_by(task_id=self.id, order=0).first()

    @property
    def get_next_unvisited_waypoint(self):
        return (
            Waypoint.query.filter_by(task_id=self.id, visited=False)
            .order_by(Waypoint.order.asc())
            .first()
        )

    @cached_property
    def path_dist_lower_bound(self):
        if not self.waypoints:
            return 0
        task_waypoints = (
            Waypoint.query.filter_by(task_id=self.id).order_by(Waypoint.order.asc()).all()
        )
        total_dist = 0
        for ind in range(1, len(task_waypoints)):
            previous_waypoint, current_waypoint = task_waypoints[ind - 1], task_waypoints[ind]
            total_dist += euclidean_dist(
                previous_waypoint.x, current_waypoint.x, previous_waypoint.y, current_waypoint.y
            )
        return total_dist

    @cached_property
    def starting_waypoint(self):
        first_order_num = min([waypoint.order for waypoint in self.waypoints])
        return list(filter(lambda task: task.order == first_order_num, self.waypoints))[0]

    def total_path_dist_lower_bound(self, start_x, start_y):
        """
        Function returns a lower bound path distance from a given starting point
        to the ending point of the task's defined waypoint path
        """
        starting_waypoint = self.starting_waypoint
        return (
            euclidean_dist(starting_waypoint.x, start_x, starting_waypoint.y, start_y)
            + self.path_dist_lower_bound
        )

    def __init__(self, priority=None, status=None, agv_id=None, drive_train_type=None):
        if priority is not None and type(priority) is Priority:
            self.priority = priority
        if status is not None and type(status) is TaskStatus:
            self.status = status
        if agv_id is not None:
            self.agv_id = agv_id
        if drive_train_type is not None:
            self.drive_train_type = drive_train_type

    def __repr__(self):
        return f"TASK:{self.id}| AGV:{self.agv_id}| status:{self.status}| priority:{self.priority}| drive_train_type: {self.drive_train_type}  | path dist LB: {self.path_dist_lower_bound}"


class Waypoint(Model):
    """
    This model servers as the internal representation for user created waypoints (effectively coordinates)

    id : A unique identifier for each Waypoint
    x : the x-coordinate position of the Waypoint
    y : the y-coordinate position of the Waypoint
    theta : the rotational direction of the Waypoint (in radians)
    order : indicates when this Waypoint should be visited (in comparison to other waypoints in the same Task)
    visited : indicates whether the Waypoint was navigated to by the AGV
    task_id : indicates which Task this waypoint belongs to
    """

    __tablename__ = "waypoint"
    id = Column(db.Integer, primary_key=True)
    x = Column(db.Float)
    y = Column(db.Float)
    theta = Column(db.Float)
    order = Column(db.Integer, default=0)
    visited = Column(db.Boolean, default=False)
    task_id = Column(db.Integer, db.ForeignKey("task.id"))

    def __init__(self, x=None, y=None, theta=None, order=None, visited=None, task=None):
        self.x = x if x is not None else 0.0
        self.y = y if y is not None else 0.0
        self.theta = theta if theta is not None else 0.0
        self.order = order if order is not None else 0
        self.visted = visited if visited is not None else False
        if task is not None:
            self.task = task

    def __repr__(self):
        return f"WAYPOINT:{self.id}| TASK:{self.task_id} | (x:{self.x},y:{self.y}, 0:{self.theta}) | order:{self.order} | visited:{self.visited}"
