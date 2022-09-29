from app.core.enums import BaseEnum


class Priority(BaseEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class TaskStatus(BaseEnum):
    INCOMPLETE = "INCOMPLETE"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"
