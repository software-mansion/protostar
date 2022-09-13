from pathlib import Path
from typing import Dict, List

import pytest

from tests.data.contracts import (
    BROKEN_CONTRACT,
    FORMATTED_CONTRACT,
    UNFORMATTED_CONTRACT,
)
from tests.integration.conftest import CreateProtostarProjectFixture, ProtostarFixture


@pytest.fixture(name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        protostar.create_files(
            {
                "to_format/formatted.cairo": FORMATTED_CONTRACT,
                "to_format/unformatted1.cairo": UNFORMATTED_CONTRACT,
                "to_format/unformatted2.cairo": UNFORMATTED_CONTRACT,
                "to_format/broken.cairo": BROKEN_CONTRACT,
            }
        )
        yield protostar


async def test_formatter_formatting(protostar: ProtostarFixture):
    summary = protostar.format(["to_format"])

    assert len(summary.broken) == 1
    assert len(summary.correct) == 1
    assert len(summary.incorrect) == 2
    assert_contents_equal("to_format/formatted.cairo", "to_format/unformatted1.cairo")


async def test_formatter_checking(protostar: ProtostarFixture):
    summary = protostar.format(["to_format"], check=True)

    assert len(summary.broken) == 1
    assert len(summary.correct) == 1
    assert len(summary.incorrect) == 2
    assert_contents_not_equal(
        "to_format/formatted.cairo", "to_format/unformatted1.cairo"
    )


async def test_formatter_output(protostar: ProtostarFixture):
    _, output = protostar.format_with_output(
        targets=["to_format"],
    )

    assert_counts_in_result(
        output,
        {
            "[UNFORMATTED]": 0,
            "[FORMATTED]": 0,
            "[BROKEN]": 1,
            "[REFORMATTED]": 2,
            "[UNCHANGED]": 0,
        },
    )


async def test_formatter_output_verbose(protostar: ProtostarFixture):
    _, output = protostar.format_with_output(targets=["to_format"], verbose=True)

    assert_counts_in_result(
        output,
        {
            "[UNFORMATTED]": 0,
            "[FORMATTED]": 0,
            "[BROKEN]": 1,
            "[REFORMATTED]": 2,
            "[UNCHANGED]": 1,
        },
    )


async def test_formatter_output_check(protostar: ProtostarFixture):
    _, output = protostar.format_with_output(
        targets=["to_format"],
        check=True,
    )

    assert_counts_in_result(
        output,
        {
            "[UNFORMATTED]": 2,
            "[FORMATTED]": 0,
            "[BROKEN]": 1,
            "[REFORMATTED]": 0,
            "[UNCHANGED]": 0,
        },
    )


async def test_formatter_output_check_verbose(
    protostar: ProtostarFixture,
):
    _, output = protostar.format_with_output(
        targets=["to_format"],
        verbose=True,
        check=True,
    )

    assert_counts_in_result(
        output,
        {
            "[UNFORMATTED]": 2,
            "[FORMATTED]": 1,
            "[BROKEN]": 1,
            "[REFORMATTED]": 0,
            "[UNCHANGED]": 0,
        },
    )


async def test_formatter_ignore_broken(protostar: ProtostarFixture):
    _, output = protostar.format_with_output(
        targets=["to_format"],
        ignore_broken=True,
    )

    assert_counts_in_result(
        output,
        {
            "[UNFORMATTED]": 0,
            "[FORMATTED]": 0,
            "[BROKEN]": 0,
            "[REFORMATTED]": 2,
            "[UNCHANGED]": 0,
        },
    )


def assert_contents_equal(filepath1: str, filepath2: str):
    assert Path(filepath1).read_text() == Path(filepath2).read_text()


def assert_contents_not_equal(filepath1: str, filepath2: str):
    assert Path(filepath1).read_text() != Path(filepath2).read_text()


def assert_count_in_result(output: List[str], key: str, count: int):
    # List instead of a Generator allows much clearer output on fail.
    assert sum([1 if (key in result) else 0 for result in output]) == count


def assert_counts_in_result(output: List[str], key_to_count: Dict[str, int]):
    for key, count in key_to_count.items():
        assert_count_in_result(output, key, count)
