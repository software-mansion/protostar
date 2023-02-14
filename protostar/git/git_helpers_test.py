from pathlib import Path

import pytest

from .git_exceptions import ProtostarGitException
from .git_helpers import run_git


def test_exception_is_descriptive(tmp_path: Path):
    run_git("init", cwd=tmp_path)

    with pytest.raises(ProtostarGitException, match="nothing to commit"):
        run_git("commit", "-m", "fail because no staged files", cwd=tmp_path)
