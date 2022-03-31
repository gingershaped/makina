from enum import Enum

class Direction(Enum):
    LEFT = 0
    DOWN = 1
    RIGHT = 2
    UP = 3

class Rotation(Enum):
    STRAIGHT = 0
    LEFT = -1
    RIGHT = 1
    UTURN = 2

class State(Enum):
    NORMAL = 0
    WAITING = 1
    READING = 2
    HALTED = 3

class ConsecutiveBehavior(Enum):
    OVERWRITE = 0
    CONCAT = 1