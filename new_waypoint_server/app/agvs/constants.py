from app.core.enums import BaseEnum


class AGVState(BaseEnum):
    READY = "READY"
    BUSY = "BUSY"
    DONE = "DONE"
    STOPPED = "STOPPED"


class AGVDriveTrainType(BaseEnum):
    MECANUM = "MECANUM"
    ACKERMANN = "ACKERMANN"
