from collections import deque
from typing import Any

from pydantic import BaseModel

from . import MISSING


class UnknownValueError(Exception):
    def __init__(self, object_name: str, message: str | None = None):
        self.object_name = object_name
        if message is None:
            message = f"{object_name} is neither True nor False, it is unknown"

        self.message = message


def path_as_parts(path: str, *, separator: str = "__") -> list[str]:
    """Convert a path string to a list of parts.

    Args:
      path: The path string.
      separator: The separator to use.

    Returns:
        A list of parts.

    Examples:
        >>> path_as_parts("a__b__c")
        ["a", "b", "c"]
    """
    return path.split(separator)


def get_path_part(path: str, index: int, *, separator: str = "__") -> str:
    """Get a part of a path string.

    Args:
        path: The path string.
        index: The index of the part to get.
        separator: The separator to use.

    Returns:
        The part at the given index.

    Examples:
        >>> get_path_part("a__b__c", 1)
        "b"
    """
    return path_as_parts(path, separator=separator)[index]


def path_popleft(path: str, *, separator: str = "__") -> tuple[str, str]:
    """Remove the first part of a path string.

    Args:
        path: The path string.
        separator: The separator to use.

    Returns:
        A tuple of the first part and the rest of the path.

    Examples:
        >>> path_popleft("a__b__c")
        ("a", "b__c")
    """
    parts = path_as_parts(path, separator=separator)
    return parts[0], separator.join(parts[1:]) if len(parts) > 1 else ""


def path_popright(path: str, *, separator: str = "__") -> tuple[str, str]:
    """Remove the last part of a path string.

    Args:
        path: The path string.
        separator: The separator to use.

    Returns:
        A tuple of the last part and the rest of the path.

    Examples:
        >>> path_popright("a__b__c")
        ("c", "a__b")
    """
    parts = path_as_parts(path, separator=separator)
    return parts[-1], separator.join(parts[:-1]) if len(parts) > 1 else ""


def getattr_path(obj, path: "str | AttrPath", *, default: Any = MISSING):
    """Get an attribute path, as defined by a string separated by '__'.

    getattr_path(foo, 'a__b__c') is roughly equivalent to foo.a.b.c but
    will short circuit to return None if something on the path is None.
    If no default value is provided AttributeError is raised if an attribute
    is missing somewhere along the path. If a default value is provided that
    value is returned.
    """
    if path == "":
        return obj
    current = obj
    attr_path = AttrPath.str_to_path(path)
    for name in attr_path:
        if default is MISSING:
            try:
                current = getattr(current, name)
            except AttributeError as e:
                msg = f"'{type(obj).__name__}' object has no attribute path '{path}', since {e}"
                raise AttributeError(msg) from e

        else:
            current = getattr(current, name, MISSING)
            if current is MISSING:
                return default
        if current is None:
            return None
    return current


def setattr_path(obj, path: str, value: Any):
    """Set an attribute path, as defined by a string separated by '__'.

    setattr_path(foo, 'a__b__c', value) is roughly equivalent to foo.a.b.c = value
    """
    current = obj
    parts = path_as_parts(path)
    for name in parts[:-1]:
        current = getattr(current, name)
    setattr(current, parts[-1], value)


LAST = object()


class AttrPath(BaseModel):
    value: str
    _separator: str = "__"
    _parts: deque[str]

    def __init__(self, **data):
        super().__init__(**data)
        self._parts = deque(self.value.split(self._separator))

    @classmethod
    def str_to_path(cls, value: "str | AttrPath") -> "AttrPath":
        if not isinstance(value, AttrPath):
            return cls(value=value)
        return value

    def __iter__(self):
        return iter(self._parts)

    def parts(self):
        return self._parts

    def pop(self, index: int = -1):
        self._parts.rotate(-index)
        value = self._parts.popleft()
        self._parts.rotate(index)
        return value

    def popleft(self):
        return self._parts.popleft()

    def get(self, index: int):
        return self._parts[index]

    def render(self):
        return self._separator.join(self._parts)

    def __str__(self):
        return self.render()

    @property
    def depth(self):
        return len(self._parts)
