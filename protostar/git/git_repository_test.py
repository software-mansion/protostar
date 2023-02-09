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

    repo_main = GitRepository.from_path(main_path)
    repo_sub = GitRepository.from_path(sub_path)

    assert repo_main.repo_path == repo_sub.repo_path

    with pytest.raises(
        InvalidGitRepositoryException, match=re.escape("is not a valid git repository.")
    ):
        GitRepository.from_path(tmp_path)
