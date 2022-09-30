import os
from pathlib import Path
import re

import pytest

from .git import Git
from .git_exceptions import GitNotFoundException, InvalidGitRepositoryException


def test_ensure_has_git(tmp_path: Path):
    Git.init(tmp_path)

    path = os.environ["PATH"]
    os.environ["PATH"] = ""

    with pytest.raises(
        GitNotFoundException, match=re.escape("Git executable not found.")
    ):
        Git.init(tmp_path)

    os.environ["PATH"] = path


def test_load_existing_repo(tmp_path: Path):
    main_path = tmp_path / "main"
    sub_path = main_path / "sub"

    sub_path.mkdir(parents=True)
    Git.init(main_path)

    repo_main = Git.load_existing_repo(main_path)
    repo_sub = Git.load_existing_repo(sub_path)

    assert repo_main.repo_path == repo_sub.repo_path

    with pytest.raises(
        InvalidGitRepositoryException, match=re.escape("is not a valid git repository.")
    ):
        Git.load_existing_repo(tmp_path)
