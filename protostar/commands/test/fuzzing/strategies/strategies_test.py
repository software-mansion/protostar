import pytest
from protostar.commands.test.fuzzing.exceptions import SearchStrategyBuildError
from .one_of import OneOfStrategyDescriptor
from .felts import FeltsStrategyDescriptor


def test_one_of_constructor_invalid_args():
    with pytest.raises(SearchStrategyBuildError) as ex:
        OneOfStrategyDescriptor("Not a StrategyDescriptor")  # type: ignore
    assert "Strategy 'one_of' takes only other strategies as arguments." == str(
        ex.value
    )


def test_one_of_constructor_no_args():
    with pytest.raises(SearchStrategyBuildError) as ex:
        OneOfStrategyDescriptor()
    assert "Strategy 'one_of' takes at least one argument." == str(ex.value)


def test_one_of_constructor_valid_args():
    OneOfStrategyDescriptor(FeltsStrategyDescriptor(), FeltsStrategyDescriptor())
