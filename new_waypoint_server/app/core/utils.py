import math


def euclidean_dist(x1, x2, y1, y2):
    """Utility function for calculating the euclidean distance"""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
