from .untokenizer import untokenize


def test_unparsing():
    result = untokenize(
        ["positional", None, 42],
        {
            "string": "foobar",
            "number": 42,
            "optional": None,
            "flag": True,
            "disabled-flag": False,
            "list": [1, 2, 3],
        },
    )

    assert result == [
        "positional",
        "42",
        "--string",
        "foobar",
        "--number",
        "42",
        "--flag",
        "--list",
        "1",
        "2",
        "3",
    ]
