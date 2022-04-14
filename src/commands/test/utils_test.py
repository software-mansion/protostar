from starkware.starknet.business_logic.execution.objects import Event
from starkware.starknet.public.abi import get_selector_from_name

from .utils import ExpectedEvent, extract_core_info_from_stark_ex_message

ERROR_DESCRIPTION_WITH_TWO_ERROR_MESSAGES = """
Error message: x must not be zero. Got x=0.
Error at pc=0:2:
Unknown value for memory cell at address 1:18.
Cairo traceback (most recent call last):
Unknown location (pc=0:22)
Unknown location (pc=0:14)
Error message: a and b must be distinct.
Unknown location (pc=0:5)
"""

ERROR_DESCRIPTION_WITH_NO_ERROR_MESSAGES = """
Error at pc=0:2:
Unknown value for memory cell at address 1:18.
Cairo traceback (most recent call last):
Unknown location (pc=0:22)
Unknown location (pc=0:14)
Unknown location (pc=0:5)
"""


def test_extracting_last_error_message():
    result = extract_core_info_from_stark_ex_message(
        ERROR_DESCRIPTION_WITH_TWO_ERROR_MESSAGES
    )
    assert result == "a and b must be distinct."


def test_failing_at_extracting_last_error_message():
    result = extract_core_info_from_stark_ex_message(
        ERROR_DESCRIPTION_WITH_NO_ERROR_MESSAGES
    )
    assert result is None


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


def test_comparing_expected_event_with_state_event():
    assert ExpectedEvent({"name": "foo", "data": [42]}).match(
        Event(keys=[get_selector_from_name("foo")], data=[42], from_address=123)
    )

    assert ExpectedEvent({"name": "foo"}).match(
        Event(keys=[get_selector_from_name("foo")], data=[42], from_address=123)
    )

    assert not ExpectedEvent({"name": "bar"}).match(
        Event(keys=[get_selector_from_name("foo")], data=[42], from_address=123)
    )

    assert not ExpectedEvent({"name": "bar", "data": [24]}).match(
        Event(keys=[get_selector_from_name("foo")], data=[42], from_address=123)
    )


def test_comparing_events():
    assert ExpectedEvent.compare_events(
        [ExpectedEvent("bar"), ExpectedEvent("baz")],
        [
            Event(keys=[get_selector_from_name("foo")], data=[42], from_address=123),
            Event(keys=[get_selector_from_name("bar")], data=[42], from_address=123),
            Event(keys=[get_selector_from_name("baz")], data=[42], from_address=123),
        ],
    )


def test_comparing_single_event():
    assert ExpectedEvent.compare_events(
        [ExpectedEvent("bar")],
        [
            Event(keys=[get_selector_from_name("foo")], data=[42], from_address=123),
            Event(keys=[get_selector_from_name("bar")], data=[42], from_address=123),
            Event(keys=[get_selector_from_name("baz")], data=[42], from_address=123),
        ],
    )


def test_comparing_events_with_emit_between():
    assert ExpectedEvent.compare_events(
        [ExpectedEvent("foo"), ExpectedEvent("baz")],
        [
            Event(keys=[get_selector_from_name("foo")], data=[42], from_address=123),
            Event(keys=[get_selector_from_name("bar")], data=[42], from_address=123),
            Event(keys=[get_selector_from_name("baz")], data=[42], from_address=123),
        ],
    )


def test_fail_compating_events():
    assert not ExpectedEvent.compare_events(
        [ExpectedEvent("bar"), ExpectedEvent("baz")],
        [
            Event(keys=[get_selector_from_name("baz")], data=[42], from_address=123),
            Event(keys=[get_selector_from_name("bar")], data=[42], from_address=123),
            Event(keys=[get_selector_from_name("foo")], data=[42], from_address=123),
        ],
    )
