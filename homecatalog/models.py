import enum
import sys
from collections.abc import Sequence, Sized
from datetime import UTC
from datetime import datetime as dt
from typing import Annotated, Generic, Self, SupportsIndex, TypeVar

import xmltodict
from pydantic import (
    AfterValidator,
    AliasChoices,
    AliasGenerator,
    AnyUrl,
    ConfigDict,
    Field,
)
from attrmagic import ClassBase as ParentClassBase, SearchBase


def remove_underscore(name: str) -> str:
    return name.replace("_", "")


def add_attribute_symbol(name: str) -> str:
    return f"@{name}"


def add_symbol_remove_underscore(name: str) -> str:
    name = remove_underscore(name)
    return add_attribute_symbol(name)


def plain(name: str) -> str:
    return name


def alias_choices(name: str) -> AliasChoices:
    choices = [
        remove_underscore,
        add_symbol_remove_underscore,
    ]

    choices_eval = (choice(name) for choice in choices)

    return AliasChoices(*choices_eval)


class ClassBase(ParentClassBase):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=alias_choices, serialization_alias=plain
        ),
        from_attributes=True,
    )


class ThingType(enum.StrEnum):
    BOARDGAME = enum.auto()
    BOARDGAMEACCESSORY = enum.auto()
    BOARDGAMEEXPANSION = enum.auto()
    RPGISSUE = enum.auto()
    RPGITEM = enum.auto()
    VIDEOGAME = enum.auto()


class NameType(enum.StrEnum):
    PRIMARY = enum.auto()
    ALTERNATE = enum.auto()


class ThingName(ClassBase):
    name_type: Annotated[NameType, Field(alias="@type")]
    value: str


class LinkType(enum.StrEnum):
    BOARDGAMEACCESSORY = enum.auto()
    BOARDGAMEARTIST = enum.auto()
    BOARDGAMECATEGORY = enum.auto()
    BOARDGAMECOMPILATION = enum.auto()
    BOARDGAMEDESIGNER = enum.auto()
    BOARDGAMEEXPANSION = enum.auto()
    BOARDGAMEFAMILY = enum.auto()
    BOARDGAMEIMPLEMENTATION = enum.auto()
    BOARDGAMEINTEGRATION = enum.auto()
    BOARDGAMEMECHANIC = enum.auto()
    BOARDGAMEPUBLISHER = enum.auto()
    BOARDGAMEVERSION = enum.auto()
    RPGARTIST = enum.auto()
    RPGCATEGORY = enum.auto()
    RPGCOMPILATION = enum.auto()
    RPGDESIGNER = enum.auto()
    RPGFAMILY = enum.auto()
    RPGPUBLISHER = enum.auto()
    RPGVERSION = enum.auto()


class Link(ClassBase):
    id: int
    link_type: Annotated[LinkType, Field(validation_alias="@type")]
    value: str


ResultValueT = TypeVar("ResultValueT")


class PollResult(ClassBase, Generic[ResultValueT]):
    num_votes: int
    value: ResultValueT


class PollOption(ClassBase, Generic[ResultValueT]):
    result: list[PollResult[ResultValueT]] = Field(default_factory=lambda: [])


class NumPlayersOption(PollOption[str]):
    num_players: int


class Poll(ClassBase, Generic[ResultValueT]):
    name: str
    title: str
    total_votes: int
    results: Sequence[NumPlayersOption | PollOption[ResultValueT]] = []

    # TODO: get the counter to work here to confirm a good count
    # @model_validator(mode="after")
    # def validate_count(self) -> Self:
    #     counted_votes = 0
    #     for option in self.results:
    #         counted_votes += sum(r.num_votes for r in option.result)
    #     if counted_votes != self.total_votes:
    #         raise ValueError(
    #             f"counted {counted_votes} != total {self.total_votes}",
    #         )
    #     return self


class Polls(SearchBase[Poll[ResultValueT]], Generic[ResultValueT]):
    pass


class SuggestedNumPlayersOption(PollOption[str]):
    num_players: int


class SuggestedNumPlayersPoll(Poll[str]):
    name: str = "suggested_numplayers"
    title: str = "Suggested Number of Players"
    options: Sequence[SuggestedNumPlayersOption] = []


def not_empty(value: Sized) -> Sized:
    if len(value) == 0:
        raise ValueError("value is empty")
    return value


class SimpleValue(ClassBase, Generic[ResultValueT]):
    value: ResultValueT


def is_not_future(value: int | None) -> None:
    if value and value > dt.now(tz=UTC).year:
        raise ValueError(f"{value} is in the future")


class YearPublished(ClassBase):
    value: Annotated[int, AfterValidator(is_not_future)]


class Thing(ClassBase):
    id: int
    thing_type: Annotated[ThingType, Field(validation_alias="@type")]
    description: str
    thumbnail: AnyUrl
    image: AnyUrl
    name: Annotated[list[ThingName], AfterValidator(not_empty)]
    year_published: YearPublished | None = None
    min_players: SimpleValue[int] | None = None
    max_players: SimpleValue[int] | None = None
    playing_time: SimpleValue[int] | None = None
    min_play_time: SimpleValue[int] | None = None
    min_age: SimpleValue[int] | None = None
    link: SearchBase[Link] = SearchBase[Link](root=[])
    poll: SearchBase[Poll] = SearchBase[SuggestedNumPlayersPoll | Poll](root=[])


T = TypeVar("T", SupportsIndex, slice)


class ThingResponse(SearchBase[Thing]):
    @classmethod
    def from_xml(cls, xml_str: str) -> Self:
        parsed = xmltodict.parse(xml_str, force_list=("results",))
        items_data = parsed["items"]["item"]

        if isinstance(items_data, dict):
            items_data = [items_data]

        items = [Thing(**item_data) for item_data in items_data]

        return cls(root=items)

    def __iter__(self):
        return self.root.__iter__()

    def __getitem__(self, item: T):
        return self.root.__getitem__(item)

    def __len__(self):
        return len(self.root)

    def index(
        self, value: Thing, start: SupportsIndex = 0, stop: SupportsIndex = sys.maxsize
    ):
        return self.root.index(value, start, stop)
