from typing import Any

import pytest

from .unparser import unparse_flag_or_arguments


@pytest.mark.parametrize(
    "value, result",
    [
        ("foo", "foo"),
        (42, "42"),
        (True, True),
        (["foo", "bar"], "foo bar"),
    ],
)
def test_unparsing_to_cli_representation(value: Any, result: str):
    assert unparse_flag_or_arguments(value) == result
