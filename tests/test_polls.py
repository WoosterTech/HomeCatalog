from pathlib import Path

import pytest
from xmltodict import parse

from homecatalog.models import ThingResponse


@pytest.fixture
def poll_xml():
    xml_path = Path("tests/fixtures/poll.xml")
    assert xml_path.exists(), f"File '{xml_path}' does not exist"
    with xml_path.open("r") as file:
        xml_file = file.read()

    return parse(xml_file)


@pytest.fixture
def bunnies_xml_str():
    xml_path = Path("tests/fixtures/bunnies.xml")
    assert xml_path.exists(), f"File '{xml_path}' does not exist"
    with xml_path.open("r") as file:
        return file.read()


def test_thing_xml(bunnies_xml_str: str):
    thing_response = ThingResponse.from_xml(bunnies_xml_str)

    assert len(thing_response) == 1
    item = thing_response[0]

    assert len(item.poll) > 0

    num_player_poll = item.poll.get(name__iexact="suggested_numplayers")

    assert num_player_poll is not None
    assert num_player_poll.total_votes == 59

    piatnik_link = item.link.get(id=63306)

    assert piatnik_link.value.endswith("Spider Bunny Promo Card")
