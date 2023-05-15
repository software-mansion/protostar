from pathlib import Path

import pytest

from tests.integration._conftest import ProtostarFixture
from tests.integration.conftest import (
    CreateProtostarProjectFixture,
    assert_cairo_test_cases,
)


@pytest.fixture(name="protostar", scope="function")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar_project:
        yield protostar_project.protostar


async def test_cairo_1_runner(protostar: ProtostarFixture, datadir: Path):
    testing_summary = await protostar.test_cairo1(
        datadir / "test_cairo1.cairo",
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "passing_test",
        ],
    )


async def test_cairo_1_runner_with_external_lib(
    protostar: ProtostarFixture, datadir: Path
):
    testing_summary = await protostar.test_cairo1(
        datadir / "test_cairo1_ext_lib.cairo",
        linked_libraries=[(datadir / "external_lib_foo", "external_lib_foo")],
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "passing_test_using_foo",
        ],
    )


async def test_cairo_1_runner_empty_suite(protostar: ProtostarFixture, datadir: Path):
    testing_summary = await protostar.test_cairo1(
        datadir / "test_cairo1_empty_suite.cairo",
    )
    assert testing_summary.test_collector_result.total_test_suites_count == 0


async def test_cairo_1_runner_multiple_suites(
    protostar: ProtostarFixture, datadir: Path
):
    testing_summary = await protostar.test_cairo1(
        datadir / "multiple_suites",
        linked_libraries=[(datadir / "external_lib_foo", "external_lib_foo")],
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=["first_test", "second_test", "third_test"],
    )


async def test_cairo_1_runner_broken_suite(protostar: ProtostarFixture, datadir: Path):
    testing_summary = await protostar.test_cairo1(
        datadir / "broken" / "test_cairo1_broken_suite.cairo",
    )
    assert len(testing_summary.broken_suites) == 1


async def test_cairo_1_runner_skip_unmarked_test(
    protostar: ProtostarFixture, datadir: Path
):
    testing_summary = await protostar.test_cairo1(
        datadir / "test_cairo1_two_cases.cairo",
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "first_test",
            "second_test",
        ],
    )


async def test_cairo_1_runner_single_case(protostar: ProtostarFixture, datadir: Path):
    test_path_str = str(datadir / "test_cairo1_two_cases.cairo")
    testing_summary = await protostar.test_cairo1(
        f"{test_path_str}::second_test",
    )
    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "second_test",
        ],
    )


async def test_cairo_1_failing(
    protostar: ProtostarFixture,
    datadir: Path,
):
    test_path_str = str(datadir / "test_cairo1_failing.cairo")

    testing_summary = await protostar.test_cairo1(
        f"{test_path_str}",
    )
    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=["test_ok"],
        expected_failed_test_cases_names=[
            "test_panic_single_value",
            "test_panic_multiple_values",
        ],
    )
