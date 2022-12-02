from .simple_table import format_as_table


def test_simple_table():
    result = format_as_table({"foo": 1, "foobar": 23})

    assert result == ["foo   : 1", "foobar: 23"]
