from decimal import Decimal
from enum import Enum, member
from typing import TYPE_CHECKING, Any, TypeVar

from pydantic_core import core_schema

from . import MISSING

if TYPE_CHECKING:
    from collections.abc import Iterable

    from pydantic import GetCoreSchemaHandler

    from . import Missing


T = TypeVar("T", float, Decimal, str)


def equals(value: T, rhs: T) -> bool:
    """Compare two values for equality."""
    return value == rhs


def not_equal(value: T, rhs: T):
    """Compare two values for inequality."""
    return value != rhs


def greater_than(value: T, rhs: T):
    """Compare two values for greater than.

    Example:
    ```
    >>> greater_than(5, 3)
    True
    >>> greater_than(3, 5)
    False
    ```

    Args:
        value: The value to compare [left-hand side]
        rhs: The value to compare against [right-hand side]
    """
    return value > rhs


def greater_than_or_equal(value: T, rhs: T):
    """Compare two values for greater than or equal to.

    Example:
    ```
    >>> greater_than_or_equal(5, 3)
    True
    >>> greater_than_or_equal(3, 5)
    False
    >>> greater_than_or_equal(3, 3)
    True
    ```

    Args:
        value: The value to compare [left-hand side]
        rhs: The value to compare against [right-hand side]
    """
    return value >= rhs


def less_than(value: T, rhs: T):
    """Compare two values for less than.

    Example:
    ```
    >>> less_than(3, 5)
    True
    >>> less_than(5, 3)
    False
    ```

    Args:
        value: The value to compare [left-hand side]
        rhs: The value to compare against [right-hand side]
    """
    return value < rhs


def less_than_or_equal_to(value: T, rhs: T):
    """Compare two values for less than or equal to.

    Example:
    ```
    >>> less_than_or_equal_to(3, 5)
    True
    >>> less_than_or_equal_to(5, 3)
    False
    >>> less_than_or_equal_to(3, 3)
    True
    ```

    Args:
        value: The value to compare [left-hand side]
        rhs: The value to compare against [right-hand side]
    """
    return value <= rhs


def in_(value: T, rhs: "Iterable[T]") -> bool:
    """Check if value is in rhs.

    Example:
    ```
    >>> in_(3, [1, 2, 3, 4, 5])
    True
    >>> in_(6, [1, 2, 3, 4, 5])
    False
    ```

    Args:
        value: The value to check
        rhs: The iterable to check against
    """
    return value in rhs


# S = TypeVar("S", str, Iterable[str])


def contains(value: str, rhs: str) -> bool:
    """Check if value contains rhs.

    Example:
    ```
    >>> contains("hello", "he")
    True
    >>> contains("hello", "hi")
    False
    ```

    Args:
        value: The value to check
        rhs: The value to check against
    """
    return rhs in value


def icontains(value: str, rhs: str) -> bool:
    """Check if value contains rhs, case-insensitive.

    Example:
    ```
    >>> icontains("hello", "he")
    True
    >>> icontains("hello", "Hi")
    False
    >>> icontains("HeLlO", "he")
    True
    ```

    Args:
        value: The value to check
        rhs: The value to check against
    """
    return rhs.lower() in value.lower()


def startswith(value: str, rhs: str) -> bool:
    """Check if value starts with rhs.

    Example:
    ```
    >>> startswith("hello", "he")
    True
    >>> startswith("the", "he")
    False
    ```

    Args:
        value: The value to check
        rhs: The value to check against
    """
    return value.startswith(rhs)


def istartswith(value: str, rhs: str) -> bool:
    """Check if value starts with rhs, case-insensitive.

    Example:
    ```
    >>> istartswith("hello", "he")
    True
    >>> istartswith("the", "He")
    False
    >>> istartswith("HELLO", "he")
    True
    ```

    Args:
        value: The value to check
        rhs: The value to check against
    """
    return value.lower().startswith(rhs.lower())


def endswith(value: str, rhs: str) -> bool:
    """Check if value ends with rhs.

    Example:
    ```
    >>> endswith("hello", "lo")
    True
    >>> endswith("the", "he")
    True
    >>> endswith("the", "th")
    False
    >>> endswith("the", "Th")
    False
    ```

    Args:
        value: The value to check
        rhs: The value to check against
    """
    return value.endswith(rhs)


def iendswith(value: str, rhs: str):
    """Check if value ends with rhs, case-insensitive.

    Example:
    ```
    >>> iendswith("hello", "LO")
    True
    >>> iendswith("the", "HE")
    True
    >>> iendswith("the", "TH")
    False
    >>> iendswith("the", "Th")
    True
    ```

    Args:
        value: The value to check
        rhs: The value to check against
    """
    return value.lower().endswith(rhs.lower())


def iequal(value: str, rhs: str):
    """Check if value is equal to rhs, case-insensitive.

    Example:
    ```
    >>> iequal("hello", "HELLO")
    True
    >>> iequal("the", "THE")
    True
    >>> iequal("the", "TH")
    False
    >>> iequal("the", "Th")
    False
    ```

    Args:
        value: The value to check
        rhs: The value to check against
    """
    return value.lower() == rhs.lower()


class Operators(Enum):
    EQ = member(equals)
    NE = member(not_equal)
    GT = member(greater_than)
    GE = member(greater_than_or_equal)
    LT = member(less_than)
    LE = member(less_than_or_equal_to)
    IN = member(in_)
    CONTAINS = member(contains)
    ICONTAINS = member(icontains)
    STARTSWITH = member(startswith)
    ISTARTSWITH = member(istartswith)
    ENDSWITH = member(endswith)
    IENDSWITH = member(iendswith)
    IEQUAL = member(iequal)

    def evaluate(self, value: T, rhs: T) -> bool:
        return self.value(value, rhs)

    @staticmethod
    def get_operator(path: str, *, default: "Operators | Missing" = MISSING):
        if not isinstance(path, str):
            msg = f"expected str, not {type(path)}"
            raise TypeError(msg)
        as_string = path.split("_")[-1]
        as_string = as_string.upper()
        for enum in Operators:
            if enum.name == as_string:
                return enum

        if default is MISSING:
            msg = f"Operator '{as_string}' not found"
            raise KeyError(msg)
        return default


class Last:
    def __repr__(self):
        return "Last"

    def __eq__(self, other):
        return isinstance(other, Last)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: "GetCoreSchemaHandler"
    ):
        return core_schema.literal_schema(["LAST"])


LAST = Last()
