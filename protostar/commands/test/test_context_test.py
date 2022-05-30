import pytest

from protostar.commands.test.test_context import TestContext
from protostar.commands.test.test_environment_exceptions import ReportedException


def test_context_supports_integers():
    context = TestContext()

    context.number = 42


def test_context_supports_strings():
    context = TestContext()

    context.string = ""


def test_context_supports_bools():
    context = TestContext()

    context.bool = False


def test_not_supporting_dicts():
    context = TestContext()

    with pytest.raises(ReportedException):
        context.number = {}
