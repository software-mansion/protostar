from typing import List

import pytest
from starkware.starknet.business_logic.execution.objects import Event
from starkware.starknet.public.abi import get_selector_from_name

from .expected_event import ExpectedEvent


def test_normalizing_expected_event_input():
    event = ExpectedEvent("foo")
    assert event.name == "foo"
    assert event.data is None

    event = ExpectedEvent({"name": "foo"})
    assert event.name == "foo"
    assert event.data is None

    event = ExpectedEvent({"name": "foo", "data": [42]})
    assert event.name == "foo"
    assert event.data == [42]


@pytest.fixture(name="create_state_event")
def create_state_event_fixture():
    # pylint: disable=dangerous-default-value
    def create_state_event(
        name: str = "foo", data: List[int] = [42], from_address: int = 123
    ) -> Event:
        return Event(
            keys=[get_selector_from_name(name)], data=data, from_address=from_address
        )

    return create_state_event


def test_comparing_expected_event_names(
    create_state_event,
):
    assert ExpectedEvent({"name": "foo"}).match(create_state_event())
    assert not ExpectedEvent({"name": "bar"}).match(create_state_event())


def test_comparing_state_events_data(create_state_event):
    assert ExpectedEvent({"name": "foo", "data": [42]}).match(create_state_event())
    assert not ExpectedEvent({"name": "foo", "data": [24]}).match(create_state_event())


def test_comparing_state_event_addresses(create_state_event):
    assert ExpectedEvent({"name": "foo", "from_address": 123}).match(
        create_state_event()
    )
    assert not ExpectedEvent({"name": "foo", "from_address": 321}).match(
        create_state_event()
    )


def test_comparing_event_lists(create_state_event):
    assert (
        ExpectedEvent.find_first_expected_event_not_included_in_state_events(
            [ExpectedEvent("bar"), ExpectedEvent("baz")],
            [
                create_state_event("foo"),
                create_state_event("bar"),
                create_state_event("baz"),
            ],
        )
        is None
    )


def test_comparing_event_list_with_one_element(create_state_event):
    assert (
        ExpectedEvent.find_first_expected_event_not_included_in_state_events(
            [ExpectedEvent("bar")],
            [
                create_state_event("foo"),
                create_state_event("bar"),
                create_state_event("baz"),
            ],
        )
        is None
    )


def test_comparing_events_with_emit_between(create_state_event):
    assert (
        ExpectedEvent.find_first_expected_event_not_included_in_state_events(
            [ExpectedEvent("foo"), ExpectedEvent("baz")],
            [
                create_state_event("foo"),
                create_state_event("bar"),
                create_state_event("baz"),
            ],
        )
        is None
    )


def test_fail_comparing_event_lists(create_state_event):
    expected_event = (
        ExpectedEvent.find_first_expected_event_not_included_in_state_events(
            [ExpectedEvent("bar"), ExpectedEvent("baz")],
            [
                create_state_event("baz"),
                create_state_event("bar"),
                create_state_event("foo"),
            ],
        )
    )
    assert expected_event is not None
    assert expected_event.name == "baz"
