import pytest

from protostar.testing.fuzzing.exceptions import SearchStrategyBuildError

from .felts import FeltsStrategyDescriptor
from .one_of import OneOfStrategyDescriptor


def test_one_of_constructor_invalid_args():
    with pytest.raises(SearchStrategyBuildError) as ex:
        OneOfStrategyDescriptor(NotImplemented)
    assert "Strategy 'one_of' takes only other strategies as arguments." == str(
        ex.value
    )


def test_one_of_constructor_no_args():
    with pytest.raises(SearchStrategyBuildError) as ex:
        OneOfStrategyDescriptor()
    assert "Strategy 'one_of' takes at least one argument." == str(ex.value)


def test_one_of_constructor_valid_args():
    OneOfStrategyDescriptor(FeltsStrategyDescriptor(), FeltsStrategyDescriptor())
