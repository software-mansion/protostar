import pickle

import pytest

from protostar.starknet import ExceptionMetadata

from .test_environment_exceptions import (
    ExpectedEventMissingException,
    ExpectedRevertException,
    ExpectedRevertMismatchException,
    ReportedException,
    RevertableException,
    StarknetRevertableException,
)

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


class MockMetadata(ExceptionMetadata):
    @property
    def name(self) -> str:
        return "mock"

    def format(self) -> str:
        return "mock"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, type(self))

    def __repr__(self) -> str:
        return "<MockMetadata>"


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


def test_matching_revertable_exception_with_no_error_type_nor_message():
    expected_ex = RevertableException()
    received_ex = RevertableException(error_type="foo", error_message="bar")

    assert expected_ex.match(received_ex)
    assert not received_ex.match(expected_ex)


def test_matching_by_the_error_type():
    ex = RevertableException(error_type="foo", error_message="bar")

    assert RevertableException().match(ex)
    assert RevertableException(error_type="foo").match(ex)
    assert not RevertableException(error_type="bar").match(ex)


def test_matching_by_the_error_message():
    ex = RevertableException(error_type="foo", error_message="bar")

    assert RevertableException().match(ex)
    assert RevertableException(error_message="bar").match(ex)
    assert not RevertableException(error_message="foo").match(ex)


def test_matching_by_the_error_messages():
    ex = RevertableException(error_type="foo", error_message=["bar", "baz"])

    assert RevertableException().match(ex)
    assert RevertableException(error_message="bar").match(ex)
    assert RevertableException(error_message="baz").match(ex)
    assert not RevertableException(error_message="foo").match(ex)
    assert RevertableException(error_message=["baz", "bar"]).match(ex)
    assert not RevertableException(error_message=["foo", "bar"]).match(ex)


def test_matching_by_partial_error_message():
    ex = RevertableException(error_type="foo", error_message=["bar", "baz"])

    assert RevertableException(error_type="foo", error_message="ba").match(ex)
    assert RevertableException(error_message="ba").match(ex)
    assert RevertableException(error_message="a").match(ex)
    assert RevertableException(error_message=["ba", "b"]).match(ex)
    assert not RevertableException(error_message=["f", "b"]).match(ex)


@pytest.mark.parametrize(
    "exception",
    [
        RevertableException(["foobar"], "TRANSACTION_FAILED"),
        StarknetRevertableException(
            error_message=["message1", "message2"],
            error_type="TRANSACTION_FAILED",
            code=400,
            details="details",
        ),
        ExpectedRevertException(RevertableException(["foo"], "BAR")),
        ExpectedRevertMismatchException(
            RevertableException(["foobar"], "FOO"),
            RevertableException(["fizzbuzz"], "BAR"),
        ),
        ExpectedEventMissingException(
            matches=[],
            missing=[],
            event_selector_to_name_map={},
        ),
    ],
    ids=lambda ex: ex.__class__.__name__,
)
def test_pickle(exception: ReportedException):
    if not exception.metadata:
        exception.metadata.append(MockMetadata())

    assert "metadata" in exception.__dict__

    pickled = pickle.dumps(exception)
    actual = pickle.loads(pickled)

    assert actual is not exception
    assert isinstance(actual, type(exception))
    assert actual == exception
