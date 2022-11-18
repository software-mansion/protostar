from typing import Any


def unparse_flag_or_arguments(value: Any):
    """Arguments from external sources need to be unparsed in order to be parsed by custom parsers."""
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    return unparse_arguments(value)


def unparse_arguments(value: Any) -> str:
    if not isinstance(value, list):
        return unparse_single_value(value)

    values = value
    unparsed_values: list[str] = []
    for val in values:
        unparsed_values.append(unparse_arguments(val))
    return " ".join(unparsed_values)


def unparse_single_value(value: Any) -> str:
    assert not isinstance(value, bool)
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        return value
    assert False, f"Value '{value}' couldn't be unparsed"
