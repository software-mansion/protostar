import re

import pytest
from starkware.cairo.lang.compiler.ast.cairo_types import TypeFelt, TypePointer

from .exceptions import FuzzingError
from .strategies.felts import FeltsStrategyDescriptor
from .strategy_inference import infer_strategy_from_cairo_type


def test_infer_strategy_from_cairo_type_felt():
    assert isinstance(
        infer_strategy_from_cairo_type("foo", TypeFelt()), FeltsStrategyDescriptor
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
