from enum import Enum, auto


class OrderStatus(Enum):
    CREATED = auto()
    ASSIGNED = auto()
    COMPLETED = auto()
