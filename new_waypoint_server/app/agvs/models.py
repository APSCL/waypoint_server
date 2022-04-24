from app.database import Column, Model, db, relationship
from app.tasks.models import Task

from .constants import AGVState


class AGV(Model):
    """
    TODO: Add model description
    """

    __tablename__ = "agv"
    id = Column(db.Integer, primary_key=True)
    ip_address = Column(db.String(50), nullable=False)
    # https://medium.com/the-andela-way/how-to-create-django-like-choices-field-in-flask-sqlalchemy-1ca0e3a3af9d
    status = Column(db.Enum(AGVState), default=AGVState.READY, nullable=False)
    # ensure this is always bounded between 0 and 100 when entering
    power = Column(db.Integer, default=100)
    tasks = relationship(
        "Task",
        backref="agv",
    )
    current_task_id = Column(db.Integer, nullable=True)
    x = Column(db.Float)
    y = Column(db.Float)
    theta = Column(db.Float)

    def __init__(
        self,
        id=None,
        ip_address=None,
        status=None,
        power=None,
        x=None,
        y=None,
        theta=None,
        current_task_id=None,
        tasks=None,
    ):
        if id is not None:
            self.id = id
        self.ip_address = ip_address if ip_address is not None else "0.0.0.0"
        self.x = x if x is not None else 0.0
        self.y = y if y is not None else 0.0
        self.theta = theta if theta is not None else 0.0
        self.current_task_id = current_task_id if current_task_id is not None else None
        if status is not None and type(status) is AGVState:
            self.status = status
        if power is not None:
            self.power = power

        # TODO: Get mutlitask assignment registration working
        # if tasks is not None:
        #     self.tasks = tasks

    def __repr__(self):
        return f"AGV | ROS_DOMAIN_ID:{self.id} | IP:{self.ip_address} | ({self.x},{self.y}) | status:{self.status}"
