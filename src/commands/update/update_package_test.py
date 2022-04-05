from os import mkdir, path
from time import sleep
from typing import Optional, cast

import pytest
from git.cmd import Git
from git.repo import Repo

from src.commands.update.update_package import update_package
from src.commands.update.updating_exceptions import PackageAlreadyUpToDateException
from src.utils.create_and_commit_sample_file import create_and_commit_sample_file

# tmpdir
# - repo
#   - packages_dir
#     - submodule (to package)
# - package_repo_dir


@pytest.fixture(name="package_name")
def fixture_package_name() -> str:
    return "foobar"


@pytest.fixture(name="repo_dir")
def fixture_repo_root_dir(tmpdir) -> str:
    return path.join(tmpdir, "repo")


@pytest.fixture(name="packages_dir")
def fixture_packages_dir(repo_dir: str) -> str:
    return path.join(repo_dir, "lib")


@pytest.fixture(name="repo")
def fixture_repo(repo_dir: str):
    return Repo().init(repo_dir)


@pytest.fixture(name="current_tag")
def fixture_current_tag() -> Optional[str]:
    return None


@pytest.fixture(name="new_tag")
def fixture_new_tag() -> Optional[str]:
    return None


@pytest.fixture(name="package_repo_dir")
def fixture_package_repo_dir(tmpdir: str) -> str:
    package_repo_dir = path.join(tmpdir, "package")
    mkdir(package_repo_dir)
    return package_repo_dir


@pytest.fixture(name="package_repo")
def fixture_package_repo(current_tag: Optional[str], package_repo_dir: str):
    package_repo = Repo().init(package_repo_dir)

    create_and_commit_sample_file(package_repo, package_repo_dir)

    if current_tag is not None:
        package_repo.create_tag(current_tag)

    return package_repo


@pytest.fixture(name="submodule")
# pylint: disable=too-many-arguments
def fixture_submodule(
    repo: Repo,
    package_name: str,
    packages_dir: str,
    package_repo_dir: str,
    current_tag: Optional[str],
    package_repo: Repo,  # pylint: disable=unused-argument
):
    package_dir = path.join(packages_dir, package_name)
    submodule = repo.create_submodule(
        package_name,
        package_dir,
        package_repo_dir,
        current_tag,
    )
    repo.git.add(submodule.path)
    repo.index.commit("add submodule")

    return submodule


# ----------------------------------- TESTS ---------------------------------- #


@pytest.mark.parametrize("current_tag", ["0.1.0"])
@pytest.mark.usefixtures("submodule")
def test_updating_specific_package_with_tag(
    package_name: str,
    repo_dir: str,
    packages_dir: str,
    package_repo_dir: str,
    package_repo: Repo,
):
    git = Git(path.join(packages_dir, package_name))
    current_tag = git.execute(["git", "describe", "--tags"])
    assert current_tag == "0.1.0"

    dummy_file_path = path.join(package_repo_dir, "bar.txt")
    assert not path.exists(dummy_file_path)
    with open(dummy_file_path, "w", encoding="utf-8") as some_file:
        some_file.write("bar")
        some_file.close()
    package_repo.git.add()
    sleep(1)  # commits are sorted with precision to seconds
    package_repo.index.commit("add bar.txt")
    package_repo.create_tag("0.1.1")

    update_package(package_name, repo_dir, packages_dir)

    new_tag = git.execute(["git", "describe", "--tags"])
    assert new_tag == "0.1.1"


@pytest.mark.parametrize("current_tag", ["0.1.0"])
@pytest.mark.usefixtures("submodule", "package_repo")
def test_package_already_up_to_date(
    package_name: str,
    repo_dir: str,
    packages_dir: str,
):
    git = Git(path.join(packages_dir, package_name))
    current_tag = git.execute(["git", "describe", "--tags"])
    assert current_tag == "0.1.0"

    with pytest.raises(PackageAlreadyUpToDateException):
        update_package(package_name, repo_dir, packages_dir)

    new_tag = git.execute(["git", "describe", "--tags"])
    assert new_tag == "0.1.0"


@pytest.mark.usefixtures("submodule")
def test_updating_specific_package_without_tag(
    package_name: str,
    repo_dir: str,
    packages_dir: str,
    package_repo: Repo,
    package_repo_dir: str,
):
    git = Git(path.join(packages_dir, package_name))

    dummy_file_path = path.join(package_repo_dir, "bar.txt")
    with open(dummy_file_path, "w", encoding="utf-8") as some_file:
        some_file.write("bar")
        some_file.close()
    package_repo.git.add()
    package_repo.index.commit("add bar.txt")

    recent_commit_hash_before_update = cast(
        str, git.execute(["git", "rev-parse", "HEAD"])
    )

    update_package(package_name, repo_dir, packages_dir)

    recent_commit_hash_after_update = cast(
        str, git.execute(["git", "rev-parse", "HEAD"])
    )

    assert recent_commit_hash_after_update is not recent_commit_hash_before_update
