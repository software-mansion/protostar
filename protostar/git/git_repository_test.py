import os
import re
from pathlib import Path

import pytest

from .git_repository import GitRepository
from .git_exceptions import GitNotFoundException, InvalidGitRepositoryException


def test_ensure_has_git(tmp_path: Path):
    GitRepository.create(tmp_path)

    path = os.environ["PATH"]
    os.environ["PATH"] = ""

    with pytest.raises(
        GitNotFoundException, match=re.escape("Git executable not found.")
    ):
        GitRepository.create(tmp_path)

    os.environ["PATH"] = path


def test_load_existing_repo(tmp_path: Path):
    main_path = tmp_path / "main"
    sub_path = main_path / "sub"

    sub_path.mkdir(parents=True)
    GitRepository.create(main_path)

    repo_main = GitRepository.from_existing(main_path)
    repo_sub = GitRepository.from_existing(sub_path)

    assert repo_main.repo_path == repo_sub.repo_path

    with pytest.raises(
        InvalidGitRepositoryException, match=re.escape("is not a valid git repository.")
    ):
        GitRepository.from_existing(tmp_path)


def test_git_status(tmp_path: Path):
    repo = GitRepository.create(tmp_path)
    file_1_path = tmp_path / "file_1.txt"
    file_2_path = tmp_path / "file_2.txt"
    file_1_path.touch()
    file_2_path.touch()

    repo.add(file_1_path)
    status = repo.get_status()

    assert status.staged_file_paths == [Path("file_1.txt")]
