from os import mkdir, path
from pathlib import Path
from time import sleep
from typing import Optional

import pytest

from protostar.commands.update.update_package import update_package
from protostar.commands.update.updating_exceptions import (
    PackageAlreadyUpToDateException,
)
from protostar.utils.create_and_commit_sample_file import create_and_commit_sample_file

from protostar.git import Git, GitRepository

# tmpdir
# - repo
#   - packages_dir
#     - submodule (to package)
# - package_repo_dir


@pytest.fixture(name="package_name")
def fixture_package_name() -> str:
    return "foobar"


@pytest.fixture(name="repo_dir")
def fixture_repo_root_dir(tmpdir) -> Path:
    return Path(tmpdir) / "repo"


@pytest.fixture(name="packages_dir")
def fixture_packages_dir(repo_dir: Path) -> Path:
    return repo_dir / "lib"


@pytest.fixture(name="repo")
def fixture_repo(repo_dir: Path):
    return Git.init(repo_dir)


@pytest.fixture(name="current_tag")
def fixture_current_tag() -> Optional[str]:
    return None


@pytest.fixture(name="new_tag")
def fixture_new_tag() -> Optional[str]:
    return None


@pytest.fixture(name="package_repo_dir")
def fixture_package_repo_dir(tmpdir: str) -> Path:
    package_repo_dir = Path(tmpdir) / "package"
    mkdir(package_repo_dir)
    return package_repo_dir


@pytest.fixture(name="package_repo")
def fixture_package_repo(current_tag: Optional[str], package_repo_dir: Path):
    package_repo = Git.init(package_repo_dir)

    create_and_commit_sample_file(package_repo, package_repo_dir)

    if current_tag is not None:
        package_repo.create_tag(current_tag)

    return package_repo


@pytest.fixture(name="submodule")
def fixture_submodule(
    repo: GitRepository,
    package_name: str,
    packages_dir: Path,
    package_repo_dir: Path,
    current_tag: Optional[str],
    package_repo: GitRepository,  # pylint: disable=unused-argument
):

    repo.add_submodule(
        url=str(package_repo_dir),
        submodule_path=packages_dir / package_name,
        name=package_name,
        tag=current_tag,
    )

    repo.add(packages_dir)
    repo.commit("add submodule")


# ----------------------------------- TESTS ---------------------------------- #


@pytest.mark.parametrize("current_tag", ["0.1.0"])
@pytest.mark.usefixtures("submodule")
def test_updating_specific_package_with_tag(
    package_name: str,
    repo_dir: Path,
    packages_dir: Path,
    package_repo_dir: Path,
    package_repo: GitRepository,
):
    repo = Git.load_existing_repo(packages_dir / package_name)
    current_tag = repo.get_tag()
    assert current_tag == "0.1.0"

    dummy_file_path = package_repo_dir / "bar.txt"
    assert not path.exists(dummy_file_path)
    with open(dummy_file_path, "w", encoding="utf-8") as some_file:
        some_file.write("bar")
        some_file.close()
    package_repo.add(package_repo.repo_path)
    sleep(1)  # commits are sorted with precision to seconds
    package_repo.commit("add bar.txt")
    package_repo.create_tag("0.1.1")

    update_package(package_name, repo_dir, packages_dir)

    new_tag = repo.get_tag()
    assert new_tag == "0.1.1"


@pytest.mark.parametrize("current_tag", ["0.1.0"])
@pytest.mark.usefixtures("submodule", "package_repo")
def test_package_already_up_to_date(
    package_name: str,
    repo_dir: Path,
    packages_dir: Path,
):
    repo = Git.load_existing_repo(packages_dir / package_name)
    current_tag = repo.get_tag()
    assert current_tag == "0.1.0"

    with pytest.raises(PackageAlreadyUpToDateException):
        update_package(package_name, repo_dir, packages_dir)

    new_tag = repo.get_tag()
    assert new_tag == "0.1.0"


@pytest.mark.usefixtures("submodule")
def test_updating_specific_package_without_tag(
    package_name: str,
    repo_dir: Path,
    packages_dir: Path,
    package_repo: GitRepository,
    package_repo_dir: Path,
):
    repo = Git.load_existing_repo(packages_dir / package_name)

    dummy_file_path = package_repo_dir / "bar.txt"
    with open(dummy_file_path, "w", encoding="utf-8") as some_file:
        some_file.write("bar")
        some_file.close()
    package_repo.add(package_repo.repo_path)
    package_repo.commit("add bar.txt")

    recent_commit_hash_before_update = repo.get_head()

    update_package(package_name, repo_dir, packages_dir)

    recent_commit_hash_after_update = repo.get_head()

    assert recent_commit_hash_after_update is not recent_commit_hash_before_update
