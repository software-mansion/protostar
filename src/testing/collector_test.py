import re
from pathlib import Path

import pytest

from src.testing.collector import TestCollector, CollectionError

current_directory = Path(__file__).parent


def test_matching_pattern():
    match_pattern = re.compile(".*nested/test_basic.*")
    collector = TestCollector(sources_directory=Path(current_directory, "examples"))
    subjects = collector.collect(match_pattern=match_pattern)
    test_names = [subject.test_path.name for subject in subjects]
    assert test_names == ["test_basic.cairo"]


def test_omitting_pattern():
    should_collect = [
        "test_basic_broken.cairo",
        "test_basic_failure.cairo",
        "test_basic.cairo",
    ]
    omit_pattern = re.compile(".*invalid.*")
    collector = TestCollector(sources_directory=Path(current_directory, "examples"))
    subjects = collector.collect(omit_pattern=omit_pattern)
    test_names = [subject.test_path.name for subject in subjects]
    for test_name in should_collect:
        assert test_name in test_names

    assert "test_invalid_syntax.cairo" not in test_names
    assert "test_no_test_functions.cairo" not in test_names


def test_breakage_upon_broken_test_file():
    match_pattern = re.compile(".*invalid/test_invalid_syntax.*")
    collector = TestCollector(sources_directory=Path(current_directory, "examples"))

    with pytest.raises(CollectionError):
        collector.collect(match_pattern=match_pattern)
