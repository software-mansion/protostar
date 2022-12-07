import pytest
import os

from pathlib import Path

from tests.e2e.conftest import ProtostarFixture, CopyFixture


def assert_contents_equal(filepath1: str, filepath2: str):
    assert Path(filepath1).read_text() == Path(filepath2).read_text()


def assert_contents_not_equal(filepath1: str, filepath2: str):
    assert Path(filepath1).read_text() != Path(filepath2).read_text()


@pytest.mark.usefixtures("init")
def test_formatting_basic(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    os.mkdir("./to_format")
    copy_fixture("formatted.cairo", "./to_format")
    copy_fixture("unformatted.cairo", "./to_format")
    copy_fixture("test_broken.cairo", "./to_format")

    result = protostar(["format", "to_format"], ignore_exit_code=True)

    assert "1 reformatted" in result
    assert "1 broken" in result
    assert "3 total" in result
    assert_contents_equal(
        "./to_format/formatted.cairo", "./to_format/unformatted.cairo"
    )


@pytest.mark.usefixtures("init")
def test_formatting_check(protostar: ProtostarFixture, copy_fixture: CopyFixture):
    os.mkdir("./to_format")
    copy_fixture("formatted.cairo", "./to_format")
    copy_fixture("unformatted.cairo", "./to_format")
    copy_fixture("test_broken.cairo", "./to_format")

    result = protostar(["format", "to_format", "--check"], ignore_exit_code=True)

    assert "1 unformatted" in result
    assert "1 broken" in result
    assert "3 total" in result
    assert_contents_not_equal(
        "./to_format/formatted.cairo", "./to_format/unformatted.cairo"
    )
