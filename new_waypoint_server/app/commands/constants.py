from app.core.enums import BaseEnum


class CommandTypes(BaseEnum):
    CANCEL_TASK = "CANCEL_TASK"
    CANCEL_AGV = "CANCEL_AGV"
    STOP_AGV = "STOP_AGV"
    START_AGV = "START_AGV"
