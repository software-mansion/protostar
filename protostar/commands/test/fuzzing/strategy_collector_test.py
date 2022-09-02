import re

import pytest
from hypothesis.strategies import SearchStrategy
from starkware.cairo.lang.compiler.ast.cairo_types import TypeFelt

from protostar.commands.test.fuzzing.exceptions import FuzzingError
from protostar.commands.test.fuzzing.strategies import (
    FeltsStrategyDescriptor,
    IntegersStrategyDescriptor,
)
from protostar.commands.test.fuzzing.strategy_collector import collect_search_strategies


# Note: Order of keys is tested here.
@pytest.mark.parametrize(
    "declared_strategies",
    [
        {},
        {
            "a": FeltsStrategyDescriptor(),
        },
        {
            "a": FeltsStrategyDescriptor(),
            "b": IntegersStrategyDescriptor(),
        },
    ],
)
def test_collect(declared_strategies):
    actual = collect_search_strategies(
        declared_strategies=declared_strategies,
        parameters={
            "a": TypeFelt(),
            "b": TypeFelt(),
        },
    )

    assert list(actual.keys()) == ["a", "b"]
    for v in actual.values():
        assert isinstance(v, SearchStrategy)


def test_collect_unknown_parameter():
    with pytest.raises(FuzzingError, match=re.escape("Unknown fuzzing parameter b.")):
        collect_search_strategies(
            declared_strategies={
                "a": FeltsStrategyDescriptor(),
                "b": FeltsStrategyDescriptor(),
            },
            parameters={"a": TypeFelt()},
        )


def test_collect_unknown_parameters():
    with pytest.raises(
        FuzzingError, match=re.escape("Unknown fuzzing parameters: b, c.")
    ):
        collect_search_strategies(
            declared_strategies={
                "a": FeltsStrategyDescriptor(),
                "b": FeltsStrategyDescriptor(),
                "c": FeltsStrategyDescriptor(),
            },
            parameters={"a": TypeFelt()},
        )


def test_collect_catches_strategy_build_error():
    with pytest.raises(
        FuzzingError,
        match=re.escape(
            "Parameter 'a' cannot be fuzzed: "
            "Strategy 'felts' can only be applied to felt parameters."
        ),
    ):
        collect_search_strategies(
            declared_strategies={
                "a": FeltsStrategyDescriptor(),
                "b": FeltsStrategyDescriptor(),
            },
            parameters={
                "a": TypeFelt().get_pointer_type(),
                "b": TypeFelt(),
            },
        )
