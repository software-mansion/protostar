# pylint: disable=unused-argument

from pathlib import Path
from typing import List

import pytest
from starkware.cairo.lang.compiler.preprocessor.preprocessor_error import (
    PreprocessorError,
)

from .test_collector import TestCollector, FunctionNameGetter
from .test_suite import TestCase, TestSuite


@pytest.fixture(name="project_root")
def project_root_fixture(tmp_path: Path) -> Path:
    return tmp_path


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


FunctionNameGetterFixture = FunctionNameGetter


@pytest.fixture(name="function_name_getter")
def function_name_getter_fixture() -> FunctionNameGetter:
    def get_function_names(file_path: Path):
        return ["test_case_a", "test_case_b", "run"]

    return get_function_names


def assert_tested_suites(test_suites: List[TestSuite], expected_file_names: List[str]):
    test_suite_names = [test_suite.test_path.name for test_suite in test_suites]
    assert set(test_suite_names) == set(expected_file_names)
    assert len(expected_file_names) == len(test_suites)


def test_is_test_suite():
    assert TestCollector.is_test_suite("ex_test.cairo")
    assert TestCollector.is_test_suite("test_ex.cairo")
    assert not TestCollector.is_test_suite("ex.cairo")
    assert not TestCollector.is_test_suite("z_test_ex.cairo")


def test_collecting_tests_from_target(
    function_name_getter: FunctionNameGetterFixture, project_root: Path
):
    test_collector = TestCollector(function_name_getter)

    result = test_collector.collect(targets=[str(project_root)])

    assert_tested_suites(
        result.test_suites, ["bar_test.cairo", "test_foo.cairo", "test_foo.cairo"]
    )
    assert result.test_cases_count == 6


def test_returning_broken_test_suites(project_root: Path):
    def get_function_names(file_path: Path) -> List[str]:
        raise PreprocessorError("")

    test_collector = TestCollector(get_function_names)
    result = test_collector.collect(targets=[str(project_root)])

    assert len(result.broken_test_suites) > 0


def test_collecting_specific_file(
    function_name_getter: FunctionNameGetterFixture, project_root: Path
):
    test_collector = TestCollector(function_name_getter)

    result = test_collector.collect([str(project_root / "foo" / "test_foo.cairo")])

    assert_tested_suites(result.test_suites, ["test_foo.cairo"])


def test_collecting_specific_function(
    function_name_getter: FunctionNameGetterFixture, project_root: Path
):
    test_collector = TestCollector(function_name_getter)

    result = test_collector.collect(
        [str(project_root / "foo" / "test_foo.cairo::test_case_a")]
    )

    assert_tested_suites(result.test_suites, ["test_foo.cairo"])
    assert result.test_cases_count == 1


def test_finding_setup_function(project_root: Path):
    def get_function_names(file_path: Path) -> List[str]:
        return ["test_main", "__setup__"]

    test_collector = TestCollector(get_function_names)

    [suite] = test_collector.collect(
        [str(project_root / "foo" / "test_foo.cairo")]
    ).test_suites

    assert suite.setup_fn_name == "__setup__"


def test_finding_setup_case_function(project_root: Path):
    def get_function_names(file_path: Path) -> List[str]:
        return ["test_main", "setup_main", "setup_dangling"]

    test_collector = TestCollector(get_function_names)

    test_path = project_root / "foo" / "test_foo.cairo"
    [suite] = test_collector.collect([str(test_path)]).test_suites

    [test_case] = suite.test_cases

    assert test_case == TestCase(
        test_path=test_path,
        test_fn_name="test_main",
        setup_fn_name="setup_main",
    )


def test_collecting_from_directory_globs(
    function_name_getter: FunctionNameGetterFixture, project_root: Path
):
    test_collector = TestCollector(function_name_getter)

    result = test_collector.collect([f"{project_root}/b*r", f"{project_root}/f*"])

    assert_tested_suites(result.test_suites, ["bar_test.cairo", "test_foo.cairo"])


def test_recursive_globs(
    function_name_getter: FunctionNameGetterFixture, project_root: Path
):
    test_collector = TestCollector(function_name_getter)

    result = test_collector.collect([f"{project_root}/**/test_foo.cairo"])

    assert_tested_suites(result.test_suites, ["test_foo.cairo", "test_foo.cairo"])


def test_collecting_specific_function_in_glob(
    function_name_getter: FunctionNameGetterFixture, project_root: Path
):
    test_collector = TestCollector(function_name_getter)

    result = test_collector.collect([f"{project_root}/**/test_foo.cairo::test_case_a"])

    assert_tested_suites(
        result.test_suites,
        ["test_foo.cairo", "test_foo.cairo"],
    )
    assert result.test_cases_count == 2


def test_multiple_globs_pointing_to_test_case(
    function_name_getter: FunctionNameGetterFixture, project_root: Path
):
    test_collector = TestCollector(function_name_getter)

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


def test_omitting_pattern_in_globs(
    function_name_getter: FunctionNameGetterFixture, project_root: Path
):
    test_collector = TestCollector(function_name_getter)

    result = test_collector.collect(
        [str(project_root)], ignored_targets=[f"{project_root}/**/test_foo.cairo"]
    )

    assert_tested_suites(result.test_suites, ["bar_test.cairo"])
    assert result.test_cases_count == 2


def test_globs_in_test_case_name(
    function_name_getter: FunctionNameGetterFixture, project_root: Path
):
    test_collector = TestCollector(function_name_getter)

    result = test_collector.collect([f"{project_root}/foo/test_foo.cairo::*b"])

    assert_tested_suites(result.test_suites, ["test_foo.cairo"])
    assert result.test_cases_count == 1
    assert result.test_suites[0].test_cases[0].test_fn_name == "test_case_b"


def test_combining_test_suites(
    function_name_getter: FunctionNameGetterFixture, project_root: Path
):
    test_collector = TestCollector(function_name_getter)

    result = test_collector.collect(
        [
            f"{project_root}/foo/test_foo.cairo::*a",
            f"{project_root}/foo/test_foo.cairo::*b",
        ]
    )

    assert_tested_suites(result.test_suites, ["test_foo.cairo"])
    assert result.test_cases_count == 2


def test_ignoring_test_cases(
    function_name_getter: FunctionNameGetterFixture, project_root: Path
):
    test_collector = TestCollector(
        function_name_getter,
    )

    result = test_collector.collect(
        [f"{project_root}/foo/test_foo.cairo"],
        ignored_targets=["::test_case_a"],
        default_test_suite_glob=str(project_root),
    )

    assert_tested_suites(result.test_suites, ["test_foo.cairo"])
    assert result.test_cases_count == 1
    assert result.test_suites[0].test_cases[0].test_fn_name == "test_case_b"


def test_empty_test_suites(
    function_name_getter: FunctionNameGetterFixture, project_root: Path
):
    test_collector = TestCollector(function_name_getter)

    result = test_collector.collect(
        [f"{project_root}/foo/test_foo.cairo::test_not_existing_test_case"],
    )

    assert_tested_suites(result.test_suites, [])


def test_testing_all_test_cases_despite_one_of_points_to_specific_test_case(
    function_name_getter: FunctionNameGetterFixture, project_root: Path
):
    test_collector = TestCollector(function_name_getter)

    result = test_collector.collect(
        [
            f"{project_root}/foo/test_foo.cairo",
            f"{project_root}/foo/test_foo.cairo::test_case_a",
        ],
    )

    assert_tested_suites(result.test_suites, ["test_foo.cairo"])
    assert result.test_cases_count == 2
