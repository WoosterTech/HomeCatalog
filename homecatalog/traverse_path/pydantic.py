import re
from collections.abc import Iterable
from typing import Annotated, Any, Generic, Self, TypeVar

from pydantic import BaseModel, BeforeValidator, RootModel

from . import MISSING
from .by_path import AttrPath, getattr_path
from .compare import Operators

T = TypeVar("T", list, None, Any)


def coerce_to_list(value: T):
    """Validator to ensure that a value is a list.

    If the `value` is not a list, it will be coerced into a list.

    If value is `None` no coercion will be done.

    Example:
    >>> coerce_to_list("foo")
    ["foo"]
    >>> coerce_to_list(["foo"])
    ["foo"]
    >>> coerce_to_list(None)
    None

    Arguments:
      value: the value to coerce

    Returns:
      a list containing the value
    """
    if not isinstance(value, list) and value is not None:
        value = [value]
    return value


PERMS = Annotated[list[str] | None, BeforeValidator(coerce_to_list)]


class ClassBase(BaseModel):
    """Base pydantic class that adds the ability to get attributes by path."""

    def getattr_path(self, path: str | AttrPath, *, default: Any = MISSING, **kwargs):
        return getattr_path(self, path, default=default, **kwargs)


SearchRoot = TypeVar("SearchRoot", bound=ClassBase)


class SearchBase(RootModel[list[SearchRoot]], Generic[SearchRoot]):
    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]

    def __setitem__(self, key, value):
        self.root[key] = value

    def get(self, *, default: Any | None = None, **kwargs) -> SearchRoot | None:
        items_list = self.filter(**kwargs)

        if len(items_list) != 1:
            return default

        return items_list[0]

    def _compare(self, item: SearchRoot, lhs: str, rhs: Any, operator: Operators):
        value = item.getattr_path(lhs)
        return operator.evaluate(value, rhs)

    def _split_kwarg(self, kwargs: dict[str, Any]) -> tuple[str, Any]:
        """Return tuple of lhs and rhs."""
        if len(kwargs) > 1:
            msg = "only one kwarg is allowed beyond default"
            raise ValueError(msg)

        return next(iter(kwargs.items()))

    def _split_lhs(self, lhs: str):
        """Return tuple of lhs and operator."""
        # pattern finds last group after last underscore
        match_pattern = re.compile(r"^(\w+)_([^_]+)$")
        matches = match_pattern.search(lhs)
        if not matches:
            raise ValueError(f"invalid path: {lhs}")

        path = AttrPath.str_to_path(matches.group(1))
        operator_name = matches.group(2).upper()
        operator = Operators[operator_name]
        return path, operator

    def _get_compare_tuple(self, **kwargs):
        """Return tuple of lhs, rhs, and operator."""
        lhs, rhs = self._split_kwarg(kwargs)
        lhs, operator = self._split_lhs(lhs)

        return lhs, rhs, operator

    def filter(self, **kwargs) -> Self:
        lhs, rhs, operator = self._get_compare_tuple(**kwargs)

        self.root = [
            item for item in self.root if self._compare(item, lhs, rhs, operator)
        ]
        return self

    def exclude(self, **kwargs) -> Self:
        lhs, rhs, operator = self._get_compare_tuple(**kwargs)

        self.root = [
            item for item in self.root if not self._compare(item, lhs, rhs, operator)
        ]

        return self

    def append(self, item: SearchRoot):
        self.root.append(item)

    def __add__(self, other: "SearchBase | Iterable[SearchRoot]") -> Self:
        match other:
            case SearchBase():
                self.root += other.root
            case Iterable():
                self.root += list(other)
            case _:
                raise NotImplementedError

        return self

    def __len__(self):
        return len(self.root)
