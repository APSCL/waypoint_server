from abc import ABC, abstractmethod

from app.tasks.constants import Priority

from .constants import TaskSchedulers


class TaskScheduler(ABC):
    """An abstract class used for implementing task scheduling algorithms within the Waypoint Server"""

    @abstractmethod
    def generate_optimal_assignments(agv, tasks):
        pass

    @abstractmethod
    def generate_optimal_assignment(agv, tasks):
        pass


class GreedyTaskSchedulerSJF(TaskScheduler):
    @classmethod
    def generate_optimal_assignment(cls, agv, tasks):
        if not tasks:
            return None
        high_priority_tasks = [task for task in tasks if task.priority == Priority.HIGH]
        med_priority_tasks = [task for task in tasks if task.priority == Priority.MEDIUM]
        low_priority_tasks = [task for task in tasks if task.priority == Priority.LOW]

        ordered_tasks = [
            task_list
            for task_list in [high_priority_tasks, med_priority_tasks, low_priority_tasks]
            if len(task_list) > 0
        ]
        tasks = ordered_tasks[0]

        start_x, start_y = agv.x, agv.y

        sorted_tasks = list(
            sorted(tasks, key=lambda task: task.total_path_dist_lower_bound(start_x, start_y))
        )

        return sorted_tasks[0]


TASK_SCHEDULER_MAP = {TaskSchedulers.GREEDY: GreedyTaskSchedulerSJF}
