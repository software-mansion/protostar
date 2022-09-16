import pytest

from protostar.commands.test.test_environment_exceptions import ReportedException

from .test_context import TestContext


def test_immutability():
    context = TestContext()

    context.number = 0
    with pytest.raises(ReportedException):
        context.number = 1
