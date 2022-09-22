import pickle

import pytest

from .cheatable_starknet_exceptions import (
    CheatcodeException,
    ExceptionMetadata,
    ReportedException,
    SimpleReportedException,
)


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


def test_get_metadata_by_type():
    class UnusedMockMetadata(ExceptionMetadata):
        @property
        def name(self) -> str:
            return "unused"

        def format(self) -> str:
            return "unused"

    ex = SimpleReportedException("foo")

    metadata = MockMetadata()
    ex.metadata.append(metadata)

    assert ex.get_metadata_by_type(MockMetadata) is metadata
    assert ex.get_metadata_by_type(UnusedMockMetadata) is None


@pytest.mark.parametrize(
    "exception",
    [
        ReportedException("x", "y", 123),
        SimpleReportedException("message"),
        CheatcodeException("foo", "bar"),
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
