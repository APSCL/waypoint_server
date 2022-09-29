from functools import cached_property

from app.core.utils import euclidean_dist
from app.database import Column, Model, db, relationship

from .constants import Priority, TaskStatus


class PseudoTask(Model):
    __tablename__ = "pseudotask"
    id = Column(db.Integer, primary_key=True)
    goal_x = Column(db.Float)
    goal_y = Column(db.Float)
    priority = Column(db.Enum(Priority), default=Priority.LOW, nullable=False)

    def __init__(self, goal_x=None, goal_y=None, priority=None):
        self.goal_y = goal_y if goal_y is not None else 0.0
        self.goal_x = goal_x if goal_x is not None else 0.0
        if priority is not None and type(priority) is Priority:
            self.priority = priority

    def __repr__(self):
        return f"PSEUDO TASK:{self.id}| priority:{self.priority} | GOAL:({self.goal_x},{self.goal_y})"


class Task(Model):
    """
    TODO: Add model description
    """

    __tablename__ = "task"
    # id will also serve as the "ordering" metric for queueing
    id = Column(db.Integer, primary_key=True)
    priority = Column(db.Enum(Priority), default=Priority.MEDIUM, nullable=False)
    status = Column(db.Enum(TaskStatus), default=TaskStatus.INCOMPLETE, nullable=False)
    waypoints = relationship(
        "Waypoint",
        backref="task",
    )
    # for the one to one field connection an agv to a task
    agv_id = Column(db.Integer, db.ForeignKey("agv.id"))

    @cached_property
    def num_waypoints(self):
        """
        TODO: Add function description
        """
        if not self.waypoints:
            return 0
        return len(self.waypoints)

    @cached_property
    def starting_waypoint(self):
        """
        TODO: Add function description
        """
        return Waypoint.query.filter_by(task_id=self.id, order=0).first()

    @property
    def get_next_unvisited_waypoint(self):
        """
        TODO: Add function description
        """
        return Waypoint.query.filter_by(task_id=self.id, visited=False).order_by(Waypoint.order.asc()).first()

    # this will not include the length of the agv to the first waypoint
    @cached_property
    def path_dist_lower_bound(self):
        """
        TODO: Add function description
        """
        if not self.waypoints:
            return 0
        task_waypoints = Waypoint.query.filter_by(task_id=self.id).order_by(Waypoint.order.asc()).all()
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
        return euclidean_dist(starting_waypoint.x, start_x, starting_waypoint.y, start_y) + self.path_dist_lower_bound

    def __init__(self, priority=None, status=None, agv=None):
        # TODO: Implement raising custom exceptions to make this more clean
        if priority is not None and type(priority) is Priority:
            self.priority = priority
        if status is not None and type(status) is TaskStatus:
            self.status = status
        if agv is not None:
            self.agv = agv

    def __repr__(self):
        return f"TASK:{self.id}| AGV:{self.agv_id}| status:{self.status}| priority:{self.priority}| path dist LB: {self.path_dist_lower_bound}"


class Waypoint(Model):
    """
    TODO: Add model description
    """

    __tablename__ = "waypoint"
    # id will also serve as the "ordering" metric for queueing
    id = Column(db.Integer, primary_key=True)
    x = Column(db.Float)
    y = Column(db.Float)
    order = Column(db.Float, default=0)
    visited = Column(db.Boolean, default=False)

    # for the many to one relationship with tasks
    task_id = Column(db.Integer, db.ForeignKey("task.id"))

    def __init__(self, x=None, y=None, order=None, visited=None, task=None):
        self.x = x if x is not None else 0.0
        self.y = y if y is not None else 0.0
        self.order = order if order is not None else 0
        self.visted = visited if visited is not None else False
        if task is not None:
            self.task = task

    def __repr__(self):
        return f"WAYPOINT:{self.id}| TASK:{self.task_id} | ({self.x},{self.y}) | order:{self.order} | visited:{self.visited}"
