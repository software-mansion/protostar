from typing import Any

import pytest

from .unparser import unparse_arguments_from_external_source


@pytest.mark.parametrize(
    "value, result",
    [
        ("foo", ["foo"]),
        (42, ["42"]),
        (True, None),
        (["foo", "bar"], ["foo", "bar"]),
        ([21, 37], ["21", "37"]),
    ],
)
def test_unparsing_to_cli_representation(value: Any, result: str):
    assert unparse_arguments_from_external_source(value) == result
