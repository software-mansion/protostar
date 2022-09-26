import re

import pytest

from protostar.starknet import KeywordOnlyArgumentCheatcodeException
from protostar.testing.fuzzing.exceptions import SearchStrategyBuildError
from .felts import FeltsStrategyDescriptor
from .one_of import OneOfStrategyDescriptor
from .short_strings import string_to_bytes_int


def test_felts_constructor_valid_args():
    FeltsStrategyDescriptor()
    FeltsStrategyDescriptor(rc_bound=True)


def test_felts_constructor_args():
    with pytest.raises(KeywordOnlyArgumentCheatcodeException):
        # pylint: disable-next=too-many-function-args
        FeltsStrategyDescriptor(True)  # type: ignore


def test_one_of_constructor_invalid_args():
    with pytest.raises(
        SearchStrategyBuildError,
        match=re.escape("Strategy 'one_of' takes only other strategies as arguments."),
    ):
        OneOfStrategyDescriptor(NotImplemented)


def test_one_of_constructor_no_args():
    with pytest.raises(
        SearchStrategyBuildError,
        match=re.escape("Strategy 'one_of' takes at least one argument."),
    ):
        OneOfStrategyDescriptor()


def test_one_of_constructor_valid_args():
    OneOfStrategyDescriptor(FeltsStrategyDescriptor(), FeltsStrategyDescriptor())


def test_short_strings_conversion():
    assert string_to_bytes_int("hello") == 448378203247
    assert hex(string_to_bytes_int("hello")) == "0x68656c6c6f"
