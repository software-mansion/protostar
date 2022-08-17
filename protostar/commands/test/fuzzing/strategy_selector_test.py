import re
from dataclasses import dataclass
from typing import Any

import pytest
from hypothesis.strategies import SearchStrategy, integers
from starkware.cairo.lang.compiler.ast.cairo_types import (
    TypeFelt,
    TypePointer,
    CairoType,
)

from protostar.commands.test.fuzzing.exceptions import (
    FuzzingError,
    SearchStrategyBuildError,
)
from protostar.commands.test.fuzzing.strategies import FeltsStrategyDescriptor
from protostar.commands.test.fuzzing.strategy_descriptor import StrategyDescriptor
from protostar.commands.test.fuzzing.strategy_selector import (
    StrategySelector,
    infer_strategy_from_cairo_type,
)


@dataclass
class StubStrategyDescriptor(StrategyDescriptor):
    def build_strategy(self, cairo_type: CairoType) -> SearchStrategy[Any]:
        return integers()


def test_pointer_parameter():
    with pytest.raises(
        FuzzingError,
        match=re.escape(
            "Parameter 'x' cannot be fuzzed: " + "Type felt* cannot be fuzzed."
        ),
    ):
        StrategySelector({"x": TypePointer(TypeFelt())})


def test_learn():
    strategy_selector = StrategySelector({"x": TypeFelt()})
    strategy0 = strategy_selector.given_strategies["x"]

    assert strategy_selector.learn("x", StubStrategyDescriptor())

    strategy1 = strategy_selector.given_strategies["x"]
    assert strategy1 is not strategy0

    assert not strategy_selector.learn("x", StubStrategyDescriptor())

    strategy2 = strategy_selector.given_strategies["x"]
    assert strategy2 is strategy1


def test_learn_unknown_parameter():
    strategy_selector = StrategySelector({})
    with pytest.raises(FuzzingError, match=re.escape("Unknown fuzzing parameter 'x'.")):
        strategy_selector.learn("x", StubStrategyDescriptor())


def test_infer_strategy_from_cairo_type_felt():
    assert infer_strategy_from_cairo_type(TypeFelt()) == FeltsStrategyDescriptor()


def test_infer_strategy_from_cairo_type_pointer():
    with pytest.raises(
        SearchStrategyBuildError, match=re.escape("Type felt* cannot be fuzzed.")
    ):
        infer_strategy_from_cairo_type(TypePointer(TypeFelt()))
