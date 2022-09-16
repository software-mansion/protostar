import pytest

from .test_context import TestContext
from .test_environment_exceptions import ReportedException


def test_immutability():
    context = TestContext()

    context.number = 0
    with pytest.raises(ReportedException):
        context.number = 1
