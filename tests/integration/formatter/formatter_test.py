import pytest

from typing import List, Dict
from pathlib import Path

from tests.integration.protostar_fixture import ProtostarFixture
from tests.data.contracts import (
    BROKEN_CONTRACT,
    FORMATTED_CONTRACT,
    UNFORMATTED_CONTRACT,
)


def assert_contents_equal(filepath1: Path, filepath2: Path):
    assert Path(filepath1).read_text() == Path(filepath2).read_text()


def assert_contents_not_equal(filepath1: Path, filepath2: Path):
    assert Path(filepath1).read_text() != Path(filepath2).read_text()


def assert_count_in_result(output: List[str], key: str, count: int):
    # List instead of a Generator allows much clearer output on fail.
    assert sum([1 if (key in result) else 0 for result in output]) == count


def assert_counts_in_result(output: List[str], key_to_count: Dict[str, int]):
    for key, count in key_to_count.items():
        assert_count_in_result(output, key, count)


@pytest.fixture(autouse=True, scope="function")
def setup(protostar: ProtostarFixture):
    protostar.init_sync()
    protostar.create_files(
        {
            "src/formatted.cairo": FORMATTED_CONTRACT,
            "src/unformatted1.cairo": UNFORMATTED_CONTRACT,
            "src/unformatted2.cairo": UNFORMATTED_CONTRACT,
            "src/broken.cairo": BROKEN_CONTRACT,
        }
    )


def get_testing_file_names(protostar: ProtostarFixture):
    return list(
        map(
            protostar.realtive_to_absolute_path,
            [
                "src/formatted.cairo",
                "src/unformatted1.cairo",
                "src/unformatted2.cairo",
                "src/broken.cairo",
            ],
        )
    )


async def test_formatter_formatting(protostar: ProtostarFixture):
    file_names = get_testing_file_names(protostar)
    summary = protostar.format(
        targets=file_names,
    )

    assert len(summary.broken) == 1
    assert len(summary.correct) == 1
    assert len(summary.incorrect) == 2
    assert_contents_equal(file_names[0], file_names[1])


async def test_formatter_checking(protostar: ProtostarFixture):
    file_names = get_testing_file_names(protostar)
    summary = protostar.format(targets=file_names, check=True)

    assert len(summary.broken) == 1
    assert len(summary.correct) == 1
    assert len(summary.incorrect) == 2
    assert_contents_not_equal(file_names[0], file_names[1])


async def test_formatter_output(protostar: ProtostarFixture):
    file_names = get_testing_file_names(protostar)
    _, output = protostar.format_with_output(
        targets=file_names,
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
    file_names = get_testing_file_names(protostar)
    _, output = protostar.format_with_output(targets=file_names, verbose=True)

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
    file_names = get_testing_file_names(protostar)
    _, output = protostar.format_with_output(
        targets=file_names,
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


async def test_formatter_output_check_verbose(protostar: ProtostarFixture):
    file_names = get_testing_file_names(protostar)
    _, output = protostar.format_with_output(
        targets=file_names,
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
    file_names = get_testing_file_names(protostar)
    _, output = protostar.format_with_output(
        targets=file_names,
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
