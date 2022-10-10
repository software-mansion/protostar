from .arg_type import StringArgType


def test_string_arg_type():
    arg_type = StringArgType()

    result = arg_type.parse("123")

    assert arg_type.get_name() == "str"
    assert isinstance(result, str)
