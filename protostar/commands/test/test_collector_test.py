from pathlib import Path
from typing import Callable, List, cast
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from starkware.cairo.lang.compiler.preprocessor.preprocessor_error import (
    PreprocessorError,
)

from protostar.commands.test.test_collector import TestCollector
from protostar.commands.test.test_suite import TestSuite
from protostar.utils.starknet_compilation import StarknetCompiler


@pytest.fixture(name="project_root")
def project_root_fixture(tmpdir) -> Path:
    return Path(tmpdir)


@pytest.fixture(name="test_suites", autouse=True)
def test_suites_fixture(project_root: Path):
    """
    - project_root
        - bar
            - bar_test.cairo
                * test_case_a
                * test_case_b
                * run
        - foo
            - test_foo.cairo
                * test_case_a
                * test_case_b
                * run
            - foo.cairo
        - baz
            - foo
                - test_foo.cairo
                    * test_case_a
                    * test_case_b
                    * run
                - foo.cairo
    """
    tmp_bar_path = project_root / "bar"
    tmp_bar_path.mkdir(exist_ok=True, parents=True)
    (tmp_bar_path / "bar_test.cairo").touch()

    tmp_foo_path = project_root / "foo"
    tmp_foo_path.mkdir(exist_ok=True, parents=True)
    (tmp_foo_path / "test_foo.cairo").touch()
    (tmp_foo_path / "foo.cairo").touch()

    tmp_baz_path = project_root / "baz"
    tmp_baz_path.mkdir(exist_ok=True, parents=True)
    tmp_foo_path = tmp_baz_path / "foo"
    tmp_foo_path.mkdir(exist_ok=True, parents=True)
    (tmp_foo_path / "test_foo.cairo").touch()
    (tmp_foo_path / "foo.cairo").touch()


@pytest.fixture(name="starknet_compiler")
def starknet_compiler_fixture(mocker: MockerFixture):
    starknet_compiler_mock = mocker.MagicMock()
    starknet_compiler_mock.get_function_names = mocker.MagicMock()

    def get_function_names(_, predicate):
        return [
            fn_name
            for fn_name in ["test_case_a", "test_case_b", "run"]
            if predicate(fn_name)
        ]

    starknet_compiler_mock.get_function_names.side_effect = get_function_names

    return starknet_compiler_mock


def assert_tested_suites(test_suites: List[TestSuite], expected_file_names: List[str]):
    test_suite_names = [test_suite.test_path.name for test_suite in test_suites]
    assert set(test_suite_names) == set(expected_file_names)
    assert len(expected_file_names) == len(test_suites)


def test_is_test_suite():
    assert TestCollector.is_test_suite("ex_test.cairo")
    assert TestCollector.is_test_suite("test_ex.cairo")
    assert not TestCollector.is_test_suite("ex.cairo")
    assert not TestCollector.is_test_suite("z_test_ex.cairo")


def test_collecting_tests_from_target(starknet_compiler, project_root: Path):
    test_collector = TestCollector(starknet_compiler)

    result = test_collector.collect(targets=[str(project_root)])

    assert_tested_suites(
        result.test_suites, ["bar_test.cairo", "test_foo.cairo", "test_foo.cairo"]
    )
    assert result.test_cases_count == 6


def test_returning_broken_test_suites(starknet_compiler, project_root):
    test_collector = TestCollector(starknet_compiler)
    cast(
        MagicMock, starknet_compiler.preprocess_contract
    ).side_effect = PreprocessorError("")

    result = test_collector.collect(targets=[str(project_root)])

    assert len(result.broken_test_suites) > 0


def test_collecting_specific_file(starknet_compiler, project_root: Path):
    test_collector = TestCollector(starknet_compiler)

    result = test_collector.collect([str(project_root / "foo" / "test_foo.cairo")])

    assert_tested_suites(result.test_suites, ["test_foo.cairo"])


def test_collecting_specific_function(starknet_compiler, project_root: Path):
    test_collector = TestCollector(starknet_compiler)

    result = test_collector.collect(
        [str(project_root / "foo" / "test_foo.cairo::test_case_a")]
    )

    assert_tested_suites(result.test_suites, ["test_foo.cairo"])
    assert result.test_cases_count == 1


def test_collector_preprocess_contracts(
    mocker: MockerFixture, starknet_compiler, project_root: Path
):
    preprocessed_contract = mocker.MagicMock()
    starknet_compiler.preprocess_contract.return_value = preprocessed_contract
    test_collector = TestCollector(starknet_compiler)

    [suite] = test_collector.collect(
        [str(project_root / "foo" / "test_foo.cairo")]
    ).test_suites
    starknet_compiler.preprocess_contract.assert_called_once()
    assert suite.preprocessed_contract == preprocessed_contract


def test_finding_setup_function(
    starknet_compiler: StarknetCompiler, project_root: Path
):
    def get_function_names(_, predicate: Callable[[str], bool]) -> List[str]:
        return list(filter(predicate, ["test_main", "__setup__"]))

    cast(
        MagicMock, starknet_compiler.get_function_names
    ).side_effect = get_function_names
    test_collector = TestCollector(starknet_compiler)

    [suite] = test_collector.collect(
        [str(project_root / "foo" / "test_foo.cairo")]
    ).test_suites

    assert suite.setup_fn_name == "__setup__"


def test_logging_collected_one_test_suite_and_one_test_case(mocker: MockerFixture):
    logger_mock = mocker.MagicMock()

    TestCollector.Result(
        test_suites=[
            TestSuite(
                test_case_names=["foo"],
                test_path=Path(),
                preprocessed_contract=mocker.MagicMock(),
            )
        ],
    ).log(logger_mock)

    cast(MagicMock, logger_mock.info).call_args_list[0][0][0].startswith(
        "Collected 1 suite, and 1 test case"
    )


def test_logging_many_test_suites_and_many_test_cases(mocker: MockerFixture):
    logger_mock = mocker.MagicMock()

    TestCollector.Result(
        test_suites=[
            TestSuite(
                test_case_names=["foo"],
                test_path=Path(),
                preprocessed_contract=mocker.MagicMock(),
            ),
            TestSuite(
                test_case_names=["foo"],
                test_path=Path(),
                preprocessed_contract=mocker.MagicMock(),
            ),
        ],
    ).log(logger_mock)

    cast(MagicMock, logger_mock.info).call_args_list[0][0][0].startswith(
        "Collected 2 suites, and 2 test cases"
    )


def test_logging_no_cases_found(mocker: MockerFixture):
    logger_mock = mocker.MagicMock()

    TestCollector.Result(
        test_suites=[],
    ).log(logger_mock)

    cast(MagicMock, logger_mock.warning).assert_called_once_with("No test cases found")


def test_collecting_from_directory_globs(starknet_compiler, project_root):
    test_collector = TestCollector(starknet_compiler)

    result = test_collector.collect([f"{project_root}/b*r", f"{project_root}/f*"])

    assert_tested_suites(result.test_suites, ["bar_test.cairo", "test_foo.cairo"])


def test_recursive_globs(starknet_compiler, project_root):
    test_collector = TestCollector(starknet_compiler)

    result = test_collector.collect([f"{project_root}/**/test_foo.cairo"])

    assert_tested_suites(result.test_suites, ["test_foo.cairo", "test_foo.cairo"])


def test_collecting_specific_function_in_glob(starknet_compiler, project_root):
    test_collector = TestCollector(starknet_compiler)

    result = test_collector.collect([f"{project_root}/**/test_foo.cairo::test_case_a"])

    assert_tested_suites(
        result.test_suites,
        ["test_foo.cairo", "test_foo.cairo"],
    )
    assert result.test_cases_count == 2


def test_multiple_globs_pointing_to_test_case(starknet_compiler, project_root):
    test_collector = TestCollector(starknet_compiler)

    result = test_collector.collect(
        [
            f"{project_root}/foo/test_foo.cairo::test_case_a",
            f"{project_root}/**/bar_test.cairo::test_case_a",
        ]
    )

    assert_tested_suites(
        result.test_suites,
        ["bar_test.cairo", "test_foo.cairo"],
    )
    assert result.test_cases_count == 2


def test_omitting_pattern_in_globs(starknet_compiler, project_root):
    test_collector = TestCollector(starknet_compiler)

    result = test_collector.collect(
        [str(project_root)], ignored_targets=[f"{project_root}/**/test_foo.cairo"]
    )

    assert_tested_suites(result.test_suites, ["bar_test.cairo"])
    assert result.test_cases_count == 2


def test_globs_in_test_case_name(starknet_compiler, project_root):
    test_collector = TestCollector(starknet_compiler)

    result = test_collector.collect([f"{project_root}/foo/test_foo.cairo::*b"])

    assert_tested_suites(result.test_suites, ["test_foo.cairo"])
    assert result.test_cases_count == 1
    assert result.test_suites[0].test_case_names[0] == "test_case_b"


def test_combining_test_suites(starknet_compiler, project_root):
    test_collector = TestCollector(starknet_compiler)

    result = test_collector.collect(
        [
            f"{project_root}/foo/test_foo.cairo::*a",
            f"{project_root}/foo/test_foo.cairo::*b",
        ]
    )

    assert_tested_suites(result.test_suites, ["test_foo.cairo"])
    assert result.test_cases_count == 2


def test_ignoring_test_cases(starknet_compiler, project_root: Path):
    test_collector = TestCollector(
        starknet_compiler,
    )

    result = test_collector.collect(
        [f"{project_root}/foo/test_foo.cairo"],
        ignored_targets=["::test_case_a"],
        default_test_suite_glob=str(project_root),
    )

    assert_tested_suites(result.test_suites, ["test_foo.cairo"])
    assert result.test_cases_count == 1
    assert result.test_suites[0].test_case_names[0] == "test_case_b"


def test_empty_test_suites(starknet_compiler, project_root: Path):
    test_collector = TestCollector(starknet_compiler)

    result = test_collector.collect(
        [f"{project_root}/foo/test_foo.cairo::test_not_existing_test_case"],
    )

    assert_tested_suites(result.test_suites, [])


def test_testing_all_test_cases_despite_one_of_points_to_specific_test_case(
    starknet_compiler, project_root: Path
):
    test_collector = TestCollector(starknet_compiler)

    result = test_collector.collect(
        [
            f"{project_root}/foo/test_foo.cairo",
            f"{project_root}/foo/test_foo.cairo::test_case_a",
        ],
    )

    assert_tested_suites(result.test_suites, ["test_foo.cairo"])
    assert result.test_cases_count == 2
