from .test_environment_exceptions import StarknetRevertableException

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
    result = StarknetRevertableException.extract_core_info_from_stark_ex_message(
        ERROR_DESCRIPTION_WITH_TWO_ERROR_MESSAGES
    )
    assert result == "a and b must be distinct."


def test_failing_at_extracting_last_error_message():
    result = StarknetRevertableException.extract_core_info_from_stark_ex_message(
        ERROR_DESCRIPTION_WITH_NO_ERROR_MESSAGES
    )
    assert result is None


def test_extracting_all_error_messages_if_stark_ex_message_is_empty():
    results = StarknetRevertableException.extract_error_messages_from_stark_ex_message(
        None
    )

    assert len(results) == 0


def test_extracting_all_error_messages_from_stark_ex_message():
    results = StarknetRevertableException.extract_error_messages_from_stark_ex_message(
        ERROR_DESCRIPTION_WITH_TWO_ERROR_MESSAGES
    )

    assert results == ["a and b must be distinct.", "x must not be zero. Got x=0."]
