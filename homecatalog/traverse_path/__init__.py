from enum import Enum


class Missing(Enum):
    token = 0


MISSING = Missing.token

__all__ = ["MISSING", "Missing"]
