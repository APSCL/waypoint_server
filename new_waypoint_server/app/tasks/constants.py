from enum import Enum

class Priority(Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2

class TaskStatus(Enum):
    INCOMPLETE = 0
    IN_PROGRESS = 1
    COMPLETE = 2
