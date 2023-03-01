from pathlib import Path

import pytest

from tests.integration._conftest import ProtostarFixture
from tests.integration.conftest import (
    CreateProtostarProjectFixture,
    assert_cairo_test_cases,
)


@pytest.fixture(name="protostar", scope="function")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        yield protostar


async def test_cairo_1_runner(
    protostar: ProtostarFixture, shared_datadir: Path, datadir: Path
):
    protostar.create_files(
        {
            "cairo_project.toml": shared_datadir / "cairo_project.toml",
            "lib.cairo": shared_datadir / "lib.cairo",
        }
    )
    testing_summary = await protostar.run_test_runner(
        datadir / "test_cairo1.cairo",
        cairo1_test_runner=True,
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "passing_test",
        ],
    )


async def test_cairo_1_runner_with_external_lib(
    protostar: ProtostarFixture, shared_datadir: Path, datadir: Path
):
    protostar.create_files(
        {
            "cairo_project.toml": shared_datadir / "cairo_project.toml",
            "lib.cairo": shared_datadir / "lib.cairo",
        }
    )

    testing_summary = await protostar.run_test_runner(
        datadir / "test_cairo1_ext_lib.cairo",
        cairo1_test_runner=True,
        cairo_path=[datadir / "external_lib_foo"],
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "passing_test_using_foo",
        ],
    )


async def test_cairo_1_runner_empty_suite(
    protostar: ProtostarFixture, shared_datadir: Path, datadir: Path
):
    protostar.create_files(
        {
            "cairo_project.toml": shared_datadir / "cairo_project.toml",
            "lib.cairo": shared_datadir / "lib.cairo",
        }
    )

    testing_summary = await protostar.run_test_runner(
        datadir / "test_cairo1_empty_suite.cairo",
        cairo1_test_runner=True,
    )
    assert testing_summary.test_collector_result.total_test_suites_count == 0


async def test_cairo_1_runner_multiple_suites(
    protostar: ProtostarFixture, shared_datadir: Path, datadir: Path
):
    protostar.create_files(
        {
            "cairo_project.toml": shared_datadir / "cairo_project.toml",
            "lib.cairo": shared_datadir / "lib.cairo",
        }
    )

    testing_summary = await protostar.run_test_runner(
        datadir / "multiple_suites",
        cairo1_test_runner=True,
        cairo_path=[datadir / "external_lib_foo"],
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=["first_test", "second_test", "third_test"],
    )


async def test_cairo_1_runner_broken_suite(
    protostar: ProtostarFixture, shared_datadir: Path, datadir: Path
):
    protostar.create_files(
        {
            "cairo_project.toml": shared_datadir / "cairo_project.toml",
            "lib.cairo": shared_datadir / "lib.cairo",
        }
    )

    testing_summary = await protostar.run_test_runner(
        datadir / "broken" / "test_cairo1_broken_suite.cairo",
        cairo1_test_runner=True,
    )
    assert len(testing_summary.broken_suites) == 1


async def test_cairo_1_runner_skip_unmarked_test(
    protostar: ProtostarFixture, shared_datadir: Path, datadir: Path
):
    protostar.create_files(
        {
            "cairo_project.toml": shared_datadir / "cairo_project.toml",
            "lib.cairo": shared_datadir / "lib.cairo",
        }
    )

    testing_summary = await protostar.run_test_runner(
        datadir / "test_cairo1_two_cases.cairo",
        cairo1_test_runner=True,
    )

    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "first_test",
            "second_test",
        ],
    )


async def test_cairo_1_runner_single_case(
    protostar: ProtostarFixture, shared_datadir: Path, datadir: Path
):
    protostar.create_files(
        {
            "cairo_project.toml": shared_datadir / "cairo_project.toml",
            "lib.cairo": shared_datadir / "lib.cairo",
        }
    )

    test_path_str = str(datadir / "test_cairo1_two_cases.cairo")
    testing_summary = await protostar.run_test_runner(
        f"{test_path_str}::second_test",
        cairo1_test_runner=True,
    )
    assert_cairo_test_cases(
        testing_summary,
        expected_passed_test_cases_names=[
            "second_test",
        ],
    )
