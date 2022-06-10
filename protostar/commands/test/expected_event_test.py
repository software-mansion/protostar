from typing import List

import pytest
from starkware.starknet.business_logic.execution.objects import Event
from starkware.starknet.public.abi import get_selector_from_name

from .expected_event import ExpectedEvent


def test_normalizing_expected_event_input():
    event = ExpectedEvent("foo")
    assert event.name == "foo"
    assert event.data is None

    event = ExpectedEvent.from_cheatcode_input_type({"name": "foo"})
    assert event.name == "foo"
    assert event.data is None

    event = ExpectedEvent.from_cheatcode_input_type({"name": "foo", "data": [42]})
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
    assert ExpectedEvent(name="foo").match(create_state_event())
    assert not ExpectedEvent(name="bar").match(create_state_event())


def test_comparing_state_events_data(create_state_event):
    assert ExpectedEvent(name="foo", data=[42]).match(create_state_event())
    assert not ExpectedEvent(name="foo", data=[24]).match(create_state_event())


def test_comparing_state_event_addresses(create_state_event):
    assert ExpectedEvent(name="foo", from_address=123).match(create_state_event())
    assert not ExpectedEvent(name="foo", from_address=321).match(create_state_event())


def test_comparing_event_lists(create_state_event):
    expected_events = [ExpectedEvent("bar"), ExpectedEvent("baz")]
    state_events = [
        create_state_event("foo"),
        create_state_event("bar"),
        create_state_event("baz"),
    ]

    matches, remaining = ExpectedEvent.match_state_events_to_expected_to_events(
        expected_events, state_events
    )
    assert not remaining
    assert matches == [
        (ExpectedEvent.MatchResult.SKIPPED, state_events[0]),
        (ExpectedEvent.MatchResult.MATCH, expected_events[0], state_events[1]),
        (ExpectedEvent.MatchResult.MATCH, expected_events[1], state_events[2]),
    ]


def test_comparing_event_list_with_one_element(create_state_event):
    expected_events = [ExpectedEvent("bar")]
    state_events = [
        create_state_event("foo"),
        create_state_event("bar"),
        create_state_event("baz"),
    ]

    matches, remaining = ExpectedEvent.match_state_events_to_expected_to_events(
        expected_events, state_events
    )
    assert not remaining
    assert matches == [
        (ExpectedEvent.MatchResult.SKIPPED, state_events[0]),
        (ExpectedEvent.MatchResult.MATCH, expected_events[0], state_events[1]),
        (ExpectedEvent.MatchResult.SKIPPED, state_events[2]),
    ]


def test_comparing_events_with_emit_between(create_state_event):
    expected_events = [ExpectedEvent("foo"), ExpectedEvent("baz")]
    state_events = [
        create_state_event("foo"),
        create_state_event("bar"),
        create_state_event("baz"),
    ]

    matches, remaining = ExpectedEvent.match_state_events_to_expected_to_events(
        expected_events, state_events
    )
    assert not remaining
    assert matches == [
        (ExpectedEvent.MatchResult.MATCH, expected_events[0], state_events[0]),
        (ExpectedEvent.MatchResult.SKIPPED, state_events[1]),
        (ExpectedEvent.MatchResult.MATCH, expected_events[1], state_events[2]),
    ]


def test_fail_comparing_event_lists(create_state_event):
    expected_events = [ExpectedEvent("baz"), ExpectedEvent("bar")]
    state_events = [
        create_state_event("foo"),
        create_state_event("bar"),
        create_state_event("baz"),
    ]

    matches, remaining = ExpectedEvent.match_state_events_to_expected_to_events(
        expected_events, state_events
    )
    assert remaining == [expected_events[1]]
    assert matches == [
        (ExpectedEvent.MatchResult.SKIPPED, state_events[0]),
        (ExpectedEvent.MatchResult.SKIPPED, state_events[1]),
        (ExpectedEvent.MatchResult.MATCH, expected_events[0], state_events[2]),
    ]
