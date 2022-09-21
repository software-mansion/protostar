import re

import pytest

from protostar.testing.fuzzing.exceptions import SearchStrategyBuildError
from . import strategies


def test_felts_constructor_valid_args():
    strategies.felts()
    strategies.felts(rc_bound=True)


def test_felts_constructor_args():
    with pytest.raises(
        SearchStrategyBuildError,
        match=re.escape("felts() takes 0 positional arguments but 1 was given"),
    ):
        # pylint: disable-next=too-many-function-args
        strategies.felts(True)  # type: ignore


def test_one_of_constructor_invalid_args():
    with pytest.raises(
        SearchStrategyBuildError,
        match=re.escape("one_of() takes only other strategies as arguments"),
    ):
        strategies.one_of(NotImplemented)


def test_one_of_constructor_no_args():
    with pytest.raises(
        SearchStrategyBuildError,
        match=re.escape("one_of() takes at least 1 positional argument"),
    ):
        strategies.one_of()


def test_one_of_constructor_valid_args():
    strategies.one_of(strategies.felts(), strategies.felts())


def test_map_with_kwarg():
    with pytest.raises(
        SearchStrategyBuildError,
        match=re.escape(
            "map() got some positional-only arguments passed as keyword arguments: 'f'"
        ),
    ):
        strategies.felts().map(f=lambda x: x)  # type: ignore


def test_filter_with_kwarg():
    with pytest.raises(
        SearchStrategyBuildError,
        match=re.escape(
            "filter() got some positional-only arguments passed as keyword arguments: 'f'"
        ),
    ):
        strategies.felts().filter(f=lambda x: x)  # type: ignore
