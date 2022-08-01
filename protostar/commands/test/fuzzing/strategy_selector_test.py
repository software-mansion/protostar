import re

import pytest
from hypothesis.strategies import integers
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


def test_parameter_names():
    strategy_selector = StrategySelector({"x": TypeFelt(), "y": TypeFelt()})
    assert list(strategy_selector.parameter_names) == ["x", "y"]


def test_contains():
    strategy_selector = StrategySelector({"x": TypeFelt()})
    assert "x" in strategy_selector
    assert "y" not in strategy_selector


def test_get_strategy_descriptor():
    strategy_selector = StrategySelector({"x": TypeFelt()})

    descriptor1 = strategy_selector.get_strategy_descriptor("x")
    assert descriptor1 == UnsignedFeltStrategyDescriptor()

    descriptor2 = strategy_selector.get_strategy_descriptor("x")
    assert descriptor2 is descriptor1


def test_get_strategy_descriptor_unknown_parameter():
    strategy_selector = StrategySelector({})
    with pytest.raises(FuzzingError, match=re.escape("Unknown fuzzing parameter 'x'.")):
        strategy_selector.get_strategy_descriptor("x")


def test_get_search_strategy():
    strategy_selector = StrategySelector({"x": TypeFelt()})

    strategy1 = strategy_selector.get_search_strategy("x")
    assert isinstance(strategy1, type(integers()))

    strategy2 = strategy_selector.get_search_strategy("x")
    assert strategy2 is strategy1


def test_get_search_strategy_unknown_parameter():
    strategy_selector = StrategySelector({})
    with pytest.raises(FuzzingError, match=re.escape("Unknown fuzzing parameter 'x'.")):
        strategy_selector.get_search_strategy("x")


def test_get_search_strategy_wraps_build_error():
    strategy_selector = StrategySelector({"x": TypePointer(TypeFelt())})
    strategy_selector.set_strategy_descriptor("x", UnsignedFeltStrategyDescriptor())
    with pytest.raises(
        FuzzingError,
        match=re.escape(
            "Parameter 'x' cannot be fuzzed: "
            "Strategy 'unsigned' can only be applied to felt parameters."
        ),
    ):
        strategy_selector.get_search_strategy("x")


def test_set_strategy_descriptor():
    strategy_selector = StrategySelector({"x": TypeFelt()})
    descriptor = SignedFeltStrategyDescriptor()
    strategy_selector.set_strategy_descriptor("x", descriptor)
    assert strategy_selector.get_strategy_descriptor("x") is descriptor


def test_set_strategy_descriptor_overrides_inferred_descriptor():
    strategy_selector = StrategySelector({"x": TypeFelt()})
    inferred_descriptor = strategy_selector.get_strategy_descriptor("x")

    overriding_descriptor = SignedFeltStrategyDescriptor()
    assert overriding_descriptor is not inferred_descriptor

    strategy_selector.set_strategy_descriptor("x", overriding_descriptor)

    overridden_descriptor1 = strategy_selector.get_strategy_descriptor("x")
    assert overridden_descriptor1 is overriding_descriptor

    # Check that if overridden again with *equal* descriptor, it does not override it.
    equal_descriptor = SignedFeltStrategyDescriptor()
    assert equal_descriptor is not overriding_descriptor
    strategy_selector.set_strategy_descriptor("x", equal_descriptor)

    overridden_descriptor2 = strategy_selector.get_strategy_descriptor("x")
    assert overridden_descriptor2 is overriding_descriptor

    not_equal_descriptor = UnsignedFeltStrategyDescriptor()
    strategy_selector.set_strategy_descriptor("x", not_equal_descriptor)

    overridden_descriptor3 = strategy_selector.get_strategy_descriptor("x")
    assert overridden_descriptor3 is not overridden_descriptor2


def test_set_strategy_descriptor_forgets_search_strategy():
    strategy_selector = StrategySelector({"x": TypeFelt()})
    strategy0 = strategy_selector.get_search_strategy("x")

    strategy_selector.set_strategy_descriptor("x", SignedFeltStrategyDescriptor())

    strategy1 = strategy_selector.get_search_strategy("x")
    assert strategy1 is not strategy0

    strategy_selector.set_strategy_descriptor("x", SignedFeltStrategyDescriptor())

    strategy2 = strategy_selector.get_search_strategy("x")
    assert strategy2 is strategy1


def test_set_strategy_descriptor_unknown_parameter():
    strategy_selector = StrategySelector({})
    with pytest.raises(FuzzingError, match=re.escape("Unknown fuzzing parameter 'x'.")):
        strategy_selector.set_strategy_descriptor("x", SignedFeltStrategyDescriptor())


def test_infer_strategy_from_cairo_type_felt():
    assert (
        infer_strategy_from_cairo_type(TypeFelt()) == UnsignedFeltStrategyDescriptor()
    )


def test_infer_strategy_from_cairo_type_pointer():
    with pytest.raises(
        SearchStrategyBuildError, match=re.escape("Type felt* cannot be fuzzed.")
    ):
        infer_strategy_from_cairo_type(TypePointer(TypeFelt()))
