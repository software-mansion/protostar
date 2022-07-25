import pytest
from protostar.commands.test.test_output_recorder import (
    format_output_name,
    OutputRecorder,
)


def test_format_output_name():
    assert format_output_name("foo") == "foo"
    assert format_output_name(("foo", 1)) == "foo:1"


def test_record_same_output_name():
    output_recorder = OutputRecorder()

    output_recorder.record("foo")

    with pytest.raises(KeyError):
        output_recorder.record("foo")


def test_record_output():
    output_recorder = OutputRecorder()

    keys = ["foo", "bar", "baz"]

    for key in keys:
        str_io = output_recorder.record(key)
        str_io.write(key.upper())
        assert output_recorder.captures[key].getvalue() == key.upper()


def test_fork():
    output_recorder = OutputRecorder()

    foo_io = output_recorder.record("foo")
    foo_io.write("FOO")

    new_output_recorder = output_recorder.fork()

    bar_io = new_output_recorder.record("bar")
    bar_io.write("BAR")

    assert "foo" in output_recorder.captures
    assert "bar" not in output_recorder.captures
    assert {"foo": "FOO", "bar": "BAR"} == new_output_recorder.get_captures()
