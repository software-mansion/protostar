from protostar.commands.test.fuzzing.fuzz_input_exception_metadata import (
    FuzzInputExceptionMetadata,
)


def test_display():
    metadata = FuzzInputExceptionMetadata(
        {"a": 340282366920938463463374607431768211456, "b": 0, "c": "abc"}
    )
    assert (
        metadata.display()
        == """
a = 340282366920938463463374607431768211456
b = 0
c = 'abc'
"""
    )


def test_display_empty():
    assert FuzzInputExceptionMetadata({}).display() == ""
