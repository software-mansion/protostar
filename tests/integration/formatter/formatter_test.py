from collections import UserList, defaultdict
from pathlib import Path

import pytest

from protostar.formatter.formatting_result import (
    FormattingResult,
    CorrectFormattingResult,
    IncorrectFormattingResult,
    BrokenFormattingResult,
)
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


class FormattingResultCollector(UserList[FormattingResult]):
    def __call__(self, result: FormattingResult):
        self.append(result)

    def count_by_type_and_check(self) -> dict[type[tuple[FormattingResult, bool]], int]:
        counts = defaultdict(lambda: 0)

        for result in self:
            counts[(type(result), result.checked_only)] += 1

        return dict(counts)


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


async def test_formatter_results(protostar: ProtostarFixture):
    results = FormattingResultCollector()
    protostar.format(
        targets=["to_format"],
        on_formatting_result=results,
    )

    assert results.count_by_type_and_check() == {
        (BrokenFormattingResult, False): 1,
        (IncorrectFormattingResult, False): 2,
    }


async def test_formatter_results_verbose(protostar: ProtostarFixture):
    results = FormattingResultCollector()
    protostar.format(
        targets=["to_format"],
        verbose=True,
        on_formatting_result=results,
    )

    assert results.count_by_type_and_check() == {
        (BrokenFormattingResult, False): 1,
        (IncorrectFormattingResult, False): 2,
        (CorrectFormattingResult, False): 1,
    }


async def test_formatter_results_check(protostar: ProtostarFixture):
    results = FormattingResultCollector()
    protostar.format(
        targets=["to_format"],
        check=True,
        on_formatting_result=results,
    )

    assert results.count_by_type_and_check() == {
        (IncorrectFormattingResult, True): 2,
        (BrokenFormattingResult, True): 1,
    }


async def test_formatter_results_check_verbose(
    protostar: ProtostarFixture,
):
    results = FormattingResultCollector()
    protostar.format(
        targets=["to_format"],
        verbose=True,
        check=True,
        on_formatting_result=results,
    )

    assert results.count_by_type_and_check() == {
        (IncorrectFormattingResult, True): 2,
        (CorrectFormattingResult, True): 1,
        (BrokenFormattingResult, True): 1,
    }


async def test_formatter_ignore_broken(protostar: ProtostarFixture):
    results = FormattingResultCollector()
    protostar.format(
        targets=["to_format"],
        ignore_broken=True,
        on_formatting_result=results,
    )

    assert results.count_by_type_and_check() == {
        (IncorrectFormattingResult, False): 2,
    }


def assert_contents_equal(filepath1: str, filepath2: str):
    assert Path(filepath1).read_text() == Path(filepath2).read_text()


def assert_contents_not_equal(filepath1: str, filepath2: str):
    assert Path(filepath1).read_text() != Path(filepath2).read_text()
