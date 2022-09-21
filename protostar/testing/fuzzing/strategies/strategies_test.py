import re

import pytest

from protostar.testing.fuzzing.exceptions import SearchStrategyBuildError
from .felts import FeltsStrategyDescriptor
from .one_of import OneOfStrategyDescriptor


def test_felts_constructor_valid_args():
    FeltsStrategyDescriptor()
    FeltsStrategyDescriptor(comparable=True)


def test_felts_constructor_args():
    with pytest.raises(TypeError):
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
