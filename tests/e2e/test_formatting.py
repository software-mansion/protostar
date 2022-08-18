import pytest
import os


def are_contents_equal(filepath1: str, filepath2: str):
    with open(filepath1, "r", encoding="utf-8") as f1:
        with open(filepath2, "r", encoding="utf-8") as f2:
            return f1.read() == f2.read()


@pytest.mark.usefixtures("init")
def test_formatting_basic(protostar, copy_fixture):
    os.mkdir("./format")
    copy_fixture("formatted.cairo", "./format")
    copy_fixture("unformatted.cairo", "./format")
    copy_fixture("test_broken.cairo", "./format")

    result = protostar(["format", "format"], ignore_exit_code=True)

    assert "1 reformatted" in result
    assert "1 broken" in result
    assert "3 total" in result
    assert are_contents_equal("./format/formatted.cairo", "./format/unformatted.cairo")


@pytest.mark.usefixtures("init")
def test_formatting_check(protostar, copy_fixture):
    os.mkdir("./format")
    copy_fixture("formatted.cairo", "./format")
    copy_fixture("unformatted.cairo", "./format")
    copy_fixture("test_broken.cairo", "./format")

    result = protostar(["format", "format", "--check"], ignore_exit_code=True)

    assert "1 unformatted" in result
    assert "1 broken" in result
    assert "3 total" in result
    assert not are_contents_equal(
        "./format/formatted.cairo", "./format/unformatted.cairo"
    )
