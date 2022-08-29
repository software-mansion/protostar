import pytest

from protostar.commands.test.test_config import TestMode, TestModeConversionException


@pytest.mark.parametrize(
    "from_mode,to_mode,expected",
    [
        (TestMode.STANDARD, TestMode.FUZZ, True),
        (TestMode.FUZZ, TestMode.STANDARD, False),
        *[(TestMode.UNDETERMINED, mode, True) for mode in TestMode],
    ],
)
def test_mode_conversion(from_mode: TestMode, to_mode: TestMode, expected: bool):
    assert from_mode.can_convert_to(to_mode) == expected

    if expected:
        assert from_mode.convert_to(to_mode) == to_mode
    else:
        with pytest.raises(TestModeConversionException):
            from_mode.convert_to(to_mode)
