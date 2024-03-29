from typing import List, Optional, Protocol

import pytest
from starkware.starknet.business_logic.execution.objects import Event
from starkware.starknet.public.abi import get_selector_from_name

from .expected_event import ExpectedEvent


class CreateStateEventFixture(Protocol):
    def __call__(
        self,
        name: str = "foo",
        data: Optional[List[int]] = None,
        from_address: int = 123,
    ) -> Event:
        ...


@pytest.fixture(name="create_state_event")
def create_state_event_fixture() -> CreateStateEventFixture:
    # pylint: disable=dangerous-default-value
    def create_state_event(
        name: str = "foo", data: Optional[List[int]] = None, from_address: int = 123
    ) -> Event:
        return Event(
            keys=[get_selector_from_name(name)],
            data=data or [42],
            from_address=from_address,
        )

    return create_state_event


def test_comparing_expected_event_names(
    create_state_event: CreateStateEventFixture,
):
    assert ExpectedEvent("foo").match(create_state_event())
    assert not ExpectedEvent("bar").match(create_state_event())


def test_comparing_state_events_data(create_state_event: CreateStateEventFixture):
    assert ExpectedEvent("foo", data=[42]).match(create_state_event())
    assert not ExpectedEvent("foo", data=[24]).match(create_state_event())


def test_comparing_state_event_addresses(create_state_event: CreateStateEventFixture):
    assert ExpectedEvent("foo", from_address=123).match(create_state_event())
    assert not ExpectedEvent("foo", from_address=321).match(create_state_event())


def test_comparing_event_lists(create_state_event: CreateStateEventFixture):
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


def test_comparing_event_list_with_one_element(
    create_state_event: CreateStateEventFixture,
):
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


def test_comparing_events_with_emit_between(
    create_state_event: CreateStateEventFixture,
):
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


def test_fail_comparing_event_lists(create_state_event: CreateStateEventFixture):
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
