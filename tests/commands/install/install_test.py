import git
import pytest
from src.commands.install import install, InstallationErrorEnum


@pytest.fixture(name="repo_url")
def fixture_repo_url():
    return "https://github.com/starkware-libs/cairo-lang"


def test_invalid_local_repository_error(tmpdir: str, repo_url: str):
    result = install(tmpdir, repo_url)

    assert result["error"] == InstallationErrorEnum.INVALID_LOCAL_REPOSITORY


def test_incorrect_url_error(tmpdir: str):
    git.Repo.init(tmpdir)

    result = install(tmpdir, "https://bitbucket.org/atlassian/python-bitbucket")

    assert result["error"] == InstallationErrorEnum.INCORRECT_URL


def test_basic_case(tmpdir: str, repo_url: str):
    git.Repo.init(tmpdir)

    result = install(tmpdir, repo_url)

    assert result["error"] is None
