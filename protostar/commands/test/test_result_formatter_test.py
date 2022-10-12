from pathlib import Path
import pytest

from protostar.testing.test_results import TestResult
from .test_result_formatter import make_path_relative_if_possible


@pytest.mark.parametrize(
    "test_path,root_path,expected",
    [
        (Path("/rrr/aaa/bbb/ccc"), Path("/rrr/aaa/bbb"), Path("ccc")),
        (Path("/rrr/ddd/bbb/ccc"), Path("/rrr/aaa/bbb"), Path("/rrr/ddd/bbb/ccc")),
        (Path("aaa/bbb/ccc"), Path("aaa/bbb"), Path("ccc")),
        (Path("ddd/bbb/ccc"), Path("aaa/bbb"), Path("ddd/bbb/ccc")),
    ],
)
def test_make_path_relative_if_possible(
    test_path: Path, root_path: Path, expected: Path
):
    test_result = TestResult(test_path)
    test_result = make_path_relative_if_possible(test_result, root_path)
    assert test_result.file_path == expected
