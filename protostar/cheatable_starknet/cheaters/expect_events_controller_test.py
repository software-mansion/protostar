from protostar.starknet import Address, Selector

from .expect_events_controller import (
    match_events,
    Event,
    should_accept_event_matching,
    SkippedEventMatching,
    AcceptedEventMatching,
)


def test_not_accepting_events():
    expected_event = Event(from_address=Address(123), key=Selector("foo"))
    emitted_event = Event(from_address=Address(123), key=Selector("bar"))

    assert not should_accept_event_matching(
        expected_event=expected_event, emitted_event=emitted_event
    )


def test_acceptance():
    expected_event = Event(from_address=Address(123), key=Selector("foo"))
    emitted_event = Event(from_address=Address(123), key=Selector("foo"))

    result = match_events(
        expected_events=[expected_event], emitted_events=[emitted_event]
    )

    assert result.should_be_accepted


def test_key_mismatch():
    expected_event = Event(from_address=Address(123), key=Selector("foo"))
    emitted_event = Event(from_address=Address(123), key=Selector("bar"))

    result = match_events(
        expected_events=[expected_event], emitted_events=[emitted_event]
    )

    assert not result.should_be_accepted


def test_address_mismatch():
    expected_event = Event(from_address=Address(123), key=Selector("foo"))
    emitted_event = Event(from_address=Address(321), key=Selector("foo"))

    result = match_events(
        expected_events=[expected_event], emitted_events=[emitted_event]
    )

    assert not result.should_be_accepted


def test_match_when_data_is_not_expected():
    expected_event = Event(from_address=Address(123), key=Selector("foo"))
    emitted_event = Event(from_address=Address(123), key=Selector("foo"), data=[42])

    result = match_events(
        expected_events=[expected_event], emitted_events=[emitted_event]
    )

    assert result.should_be_accepted


def test_data_mismatch():
    expected_event = Event(from_address=Address(123), key=Selector("foo"), data=[24])
    emitted_event = Event(from_address=Address(123), key=Selector("foo"), data=[42])

    result = match_events(
        expected_events=[expected_event], emitted_events=[emitted_event]
    )

    assert not result.should_be_accepted


def test_skip_at_front():
    expected_events = [
        Event(from_address=Address(123), key=Selector(name)) for name in ["bar", "baz"]
    ]
    emitted_events = [
        Event(from_address=Address(123), key=Selector(name))
        for name in ["foo", "bar", "baz"]
    ]

    result = match_events(
        expected_events=expected_events, emitted_events=emitted_events
    )

    assert result.should_be_accepted
    assert isinstance(result.event_matchings[0], SkippedEventMatching)
    assert isinstance(result.event_matchings[1], AcceptedEventMatching)
    assert isinstance(result.event_matchings[2], AcceptedEventMatching)


def test_skip_on_front_and_end():
    expected_events = [Event(from_address=Address(123), key=Selector("bar"))]
    emitted_events = [
        Event(from_address=Address(123), key=Selector(name))
        for name in ["foo", "bar", "baz"]
    ]

    result = match_events(
        expected_events=expected_events, emitted_events=emitted_events
    )

    assert result.should_be_accepted
    assert isinstance(result.event_matchings[0], SkippedEventMatching)
    assert isinstance(result.event_matchings[1], AcceptedEventMatching)
    assert isinstance(result.event_matchings[2], SkippedEventMatching)


def test_skip_between():
    expected_events = [
        Event(from_address=Address(123), key=Selector(name)) for name in ["foo", "baz"]
    ]
    emitted_events = [
        Event(from_address=Address(123), key=Selector(name))
        for name in ["foo", "bar", "baz"]
    ]

    result = match_events(
        expected_events=expected_events, emitted_events=emitted_events
    )

    assert result.should_be_accepted
    assert isinstance(result.event_matchings[0], AcceptedEventMatching)
    assert isinstance(result.event_matchings[1], SkippedEventMatching)
    assert isinstance(result.event_matchings[2], AcceptedEventMatching)


def test_order_impact():
    expected_events = [
        Event(from_address=Address(123), key=Selector(name)) for name in ["baz", "foo"]
    ]
    emitted_events = [
        Event(from_address=Address(123), key=Selector(name))
        for name in ["foo", "bar", "baz"]
    ]

    result = match_events(
        expected_events=expected_events, emitted_events=emitted_events
    )

    assert not result.should_be_accepted
    assert isinstance(result.event_matchings[0], SkippedEventMatching)
    assert isinstance(result.event_matchings[1], SkippedEventMatching)
    assert isinstance(result.event_matchings[2], AcceptedEventMatching)
