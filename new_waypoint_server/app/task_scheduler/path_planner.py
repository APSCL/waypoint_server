from abc import ABC, abstractmethod


# abstract class generating optimal on a fixed coordinate plane goes here
class PathPlanner(ABC):
    @abstractmethod
    def generate_optimal_path(start_x, start_y, goal_x, goal_y):
        pass
