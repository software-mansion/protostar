import re

import pytest
from starkware.cairo.lang.compiler.ast.cairo_types import (
    TypeFelt,
    TypePointer,
    TypeStruct,
)
from starkware.cairo.lang.compiler.scoped_name import ScopedName

from .exceptions import FuzzingError
from .strategies import FeltsStrategyDescriptor, Uint256StrategyDescriptor
from .strategy_inference import infer_strategy_from_cairo_type


def test_infer_strategy_from_cairo_type_felt():
    assert isinstance(
        infer_strategy_from_cairo_type("foo", TypeFelt()), FeltsStrategyDescriptor
    )


def test_infer_strategy_from_cairo_type_struct():
    assert isinstance(
        infer_strategy_from_cairo_type(
            "foo",
            TypeStruct(
                scope=ScopedName.from_string("starkware.cairo.common.uint256.Uint256")
            ),
        ),
        Uint256StrategyDescriptor,
    )


def test_infer_strategy_from_cairo_type_pointer():
    with pytest.raises(
        FuzzingError,
        match=re.escape(
            "Parameter 'foo' cannot be fuzzed automatically, "
            "because Protostar cannot infer fuzzing strategy for type felt*."
        ),
    ):
        infer_strategy_from_cairo_type("foo", TypePointer(TypeFelt()))
