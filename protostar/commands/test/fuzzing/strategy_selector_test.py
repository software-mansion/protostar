import re

import pytest
from starkware.cairo.lang.compiler.ast.cairo_types import TypeFelt, TypePointer

from protostar.commands.test.fuzzing.exceptions import FuzzingError
from protostar.commands.test.fuzzing.strategies.felt import (
    UnsignedFeltStrategyDescriptor,
    SignedFeltStrategyDescriptor,
)
from protostar.commands.test.fuzzing.strategy_descriptor import SearchStrategyBuildError
from protostar.commands.test.fuzzing.strategy_selector import (
    StrategySelector,
    infer_strategy_from_cairo_type,
)


def test_pointer_parameter():
    with pytest.raises(
        FuzzingError,
        match=re.escape(
            "Parameter 'x' cannot be fuzzed: " "Type felt* cannot be fuzzed."
        ),
    ):
        StrategySelector({"x": TypePointer(TypeFelt())})


def test_learn():
    strategy_selector = StrategySelector({"x": TypeFelt()})
    strategy0 = strategy_selector.given_strategies["x"]

    assert strategy_selector.learn("x", SignedFeltStrategyDescriptor())

    strategy1 = strategy_selector.given_strategies["x"]
    assert strategy1 is not strategy0

    assert not strategy_selector.learn("x", SignedFeltStrategyDescriptor())

    strategy2 = strategy_selector.given_strategies["x"]
    assert strategy2 is strategy1


def test_learn_unknown_parameter():
    strategy_selector = StrategySelector({})
    with pytest.raises(FuzzingError, match=re.escape("Unknown fuzzing parameter 'x'.")):
        strategy_selector.learn("x", SignedFeltStrategyDescriptor())


def test_infer_strategy_from_cairo_type_felt():
    assert (
        infer_strategy_from_cairo_type(TypeFelt()) == UnsignedFeltStrategyDescriptor()
    )


def test_infer_strategy_from_cairo_type_pointer():
    with pytest.raises(
        SearchStrategyBuildError, match=re.escape("Type felt* cannot be fuzzed.")
    ):
        infer_strategy_from_cairo_type(TypePointer(TypeFelt()))
