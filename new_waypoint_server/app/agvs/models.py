from app.database import Column, Model, db, relationship

from .constants import AGVDriveTrainType, AGVState


class AGV(Model):
    """
    This model serves as an internal representation for each running and registered AGV (Autonomous Guided Vehicle)
    in the Multiple AGV System.

    id : A unique identifier for each AGV
    ip_address : the LAN ip address of the registered AGV
    status : the current part of the navigation process the AGV is currently in (can be READY, BUSY, DONE, STOPPED)
    drive_train_type : the drive train model the AGV possesses
    power : denotes how much power the AGV currently has (bounded between 0 and 100)
    tasks : a relational link to all the Tasks the AGV has or is currently executing
    current_task_id : denotes the id of the Task the AGV is currently executing
    x : the current x-coordinate position of the AGV
    y : the current y-coordinate position of the AGV
    theta : the current rotational direction of the AGV (in radians)
    """

    __tablename__ = "agv"
    id = Column(db.Integer, primary_key=True)
    ip_address = Column(db.String(50), nullable=False)
    # NOTE: reference for the "status" db field used below: https://medium.com/the-andela-way/how-to-create-django-like-choices-field-in-flask-sqlalchemy-1ca0e3a3af9d
    status = Column(db.Enum(AGVState), default=AGVState.READY, nullable=False)
    drive_train_type = Column(
        db.Enum(AGVDriveTrainType), default=AGVDriveTrainType.ACKERMANN, nullable=False
    )
    power = Column(db.Integer, default=100)
    tasks = relationship(
        "Task",
        backref="agv",
        lazy="joined",
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
        drive_train_type=None,
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
        if drive_train_type is not None:
            self.drive_train_type = drive_train_type

    def __repr__(self):
        return f"AGV | ID:{self.id} | DRIVETRAIN: {self.drive_train_type} | IP:{self.ip_address} | (x:{self.x},y:{self.y}, 0:{self.theta}) | status:{self.status}"
