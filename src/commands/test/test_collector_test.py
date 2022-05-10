import shutil
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from src.commands.test.test_collector import TestCollector
from src.utils.starknet_compilation import StarknetCompiler

CURRENT_DIR = Path(__file__).parent


@pytest.fixture(name="project_root")
def project_root_fixture(tmpdir) -> Path:
    return Path(tmpdir)


@pytest.fixture(name="test_files", autouse=True)
def test_files_fixture(project_root: Path):
    """
    - tmpdir
    - src
        - test_basic.cairo
    - foo
        - test_foo.cairo
    """
    tmp_src_path = project_root / "src"
    tmp_src_path.mkdir(exist_ok=True, parents=True)
    tmp_foo_path = project_root / "foo"
    tmp_foo_path.mkdir(exist_ok=True, parents=True)

    shutil.copyfile(
        CURRENT_DIR / "examples" / "basic" / "test_basic.cairo",
        tmp_src_path / "test_basic.cairo",
    )

    shutil.copyfile(
        CURRENT_DIR / "examples" / "basic" / "test_basic.cairo",
        tmp_foo_path / "test_foo.cairo",
    )


def test_is_test_file():
    assert not TestCollector.is_test_file("ex.cairo")
    assert TestCollector.is_test_file("ex_test.cairo")
    assert TestCollector.is_test_file("test_ex.cairo")
    assert not TestCollector.is_test_file("z_test_ex.cairo")


def test_collecting_tests_from_target(mocker: MockerFixture, project_root):
    starknet_compiler_mock = mocker.MagicMock()
    starknet_compiler_mock.get_functions.return_value = [
        StarknetCompiler.AbiElement(
            name="test_foo", type="function", inputs=[], outputs=[]
        )
    ]
    test_collector = TestCollector(starknet_compiler_mock)

    result = test_collector.collect(target=project_root / "src")

    test_file_names = [
        test_subject.test_path.name for test_subject in result.test_subjects
    ]

    assert set(test_file_names) == set(["test_basic.cairo"])
    assert result.test_cases_count == 1


# def test_matching_pattern():
#     match_pattern = re.compile("test_basic.*")
#     collector = TestCollector(
#         target=Path(current_directory, "examples"),
#         include_paths=[str(Path(current_directory, "examples"))],
#     )
#     subjects = collector.collect(match_pattern=match_pattern)
#     test_names = [subject.test_path.name for subject in subjects]
#     assert set(test_names) == set(
#         ["test_basic.cairo", "test_basic_broken.cairo", "test_basic_failure.cairo"]
#     )


# def test_omitting_pattern():
#     should_collect = [
#         "test_basic_broken.cairo",
#         "test_basic_failure.cairo",
#         "test_basic_failure.cairo",
#         "test_basic.cairo",
#         "test_proxy.cairo",
#         "test_cheats.cairo",
#         "test_expect_events.cairo",
#     ]
#     omit_pattern = re.compile(".*invalid.*")
#     collector = TestCollector(
#         target=Path(current_directory, "examples"),
#         include_paths=[str(Path(current_directory, "examples"))],
#     )
#     subjects = collector.collect(omit_pattern=omit_pattern)
#     test_names = [subject.test_path.name for subject in subjects]

#     assert set(test_names) == set(should_collect)

#     assert "test_invalid_syntax.cairo" not in test_names
#     assert "test_no_test_functions.cairo" not in test_names


# def test_breakage_upon_broken_test_file():
#     match_pattern = re.compile("test_invalid_syntax.*")
#     collector = TestCollector(
#         target=Path(current_directory, "examples", "invalid"),
#         include_paths=[str(Path(current_directory, "examples"))],
#     )

#     with pytest.raises(CollectionError):
#         collector.collect(match_pattern=match_pattern)


# def test_collect_specific_file():
#     collector = TestCollector(
#         target=Path(current_directory, "examples", "nested", "test_basic.cairo"),
#         include_paths=[str(Path(current_directory, "examples"))],
#     )
#     subjects = collector.collect()
#     test_names = [subject.test_path.name for subject in subjects]
#     assert test_names == ["test_basic.cairo"]


# def test_collect_specific_function():
#     collector = TestCollector(
#         target=Path(
#             current_directory,
#             "examples",
#             "nested",
#             "test_basic.cairo::test_call_not_deployed",
#         ),
#         include_paths=[str(Path(current_directory, "examples"))],
#     )
#     subjects = collector.collect()
#     test_names = [subject.test_path.name for subject in subjects]
#     assert test_names == ["test_basic.cairo"]
#     assert len(subjects[0].test_functions) == 1
