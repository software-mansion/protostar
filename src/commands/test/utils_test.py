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
