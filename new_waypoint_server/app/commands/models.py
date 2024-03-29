from app.database import Column, Model, db, relationship

from .constants import CommandTypes


class Command(Model):
    """
    This model serves as a way to store client issued commands for AGVs

    id : A unique identifier for each Command
    agv_id : indicates which AGV a command should be assigned to
    task_id : indicates which Task a command is refering to (ie - used for CANCEL_TASK)
    type : the type of command issued (can be CANCEL_TASK, CANCEL_AGV, STOP_AGV, START_AGV)
    processed : indicates whether the command has been correctly assigned and executed
    """

    __tablename__ = "command"
    id = Column(db.Integer, primary_key=True)
    agv_id = Column(db.Integer, nullable=True)
    task_id = Column(db.Integer, nullable=True)
    type = Column(db.Enum(CommandTypes), nullable=True)
    processed = Column(db.Boolean, default=False)

    def __init__(self, agv_id=None, task_id=None, type=None, processed=None):
        self.agv_id = agv_id
        self.task_id = task_id
        self.type = type if type is not None else CommandTypes.CANCEL_AGV
        self.processed = processed if processed is not None else False

    def __repr__(self):
        return f"COMMAND:{self.id} | type:{str(self.type)} | processed:{self.processed}"
