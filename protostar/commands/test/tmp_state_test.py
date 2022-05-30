import pytest

from protostar.commands.test.test_environment_exceptions import ReportedException
from protostar.commands.test.tmp_state import TmpState


def test_tmp_state_supports_integers():
    tmp_state = TmpState()

    tmp_state.number = 42


def test_tmp_state_supports_strings():
    tmp_state = TmpState()

    tmp_state.string = ""


def test_tmp_state_supports_bools():
    tmp_state = TmpState()

    tmp_state.bool = False


def test_not_supporting_dicts():
    tmp_state = TmpState()

    with pytest.raises(ReportedException):
        tmp_state.number = {}


def test_should_fail_when_reading_undefined_value():
    tmp_state = TmpState()

    with pytest.raises(ReportedException):
        # pylint: disable=pointless-statement
        tmp_state.foobar
