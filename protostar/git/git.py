import subprocess
import re
import os.path
from typing import Dict, Optional
from pathlib import Path
from functools import wraps

from protostar.utils.package_info import PackageInfo
from protostar.protostar_exception import ProtostarException

# pylint: disable=subprocess-run-check

# set to true when debugging
GIT_VERBOSE = False
SHARED_KWARGS = (
    {"check": True}
    if GIT_VERBOSE
    else {
        "check": True,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }
)

DEFAULT_CREDENTIALS = [
    "-c",
    'user.name="Protostar"',
    "-c",
    'user.email="protostar@protostar.protostar"',
]


class ProtostarGitException(ProtostarException):
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__("Error while executing Git command:\n" + message, details)


class InvalidGitRepositoryException(ProtostarGitException):
    pass


class GitNotFoundException(ProtostarGitException):
    pass


def wrap_git_exception(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except subprocess.CalledProcessError as ex:
            raise ProtostarGitException(str(ex)) from ex

    return wrapper


class Git:
    @staticmethod
    def init(path_to_repo: Path):
        assert_has_git()
        path_to_repo.mkdir(parents=True, exist_ok=True)
        repo = GitRepository(path_to_repo)
        repo.init()
        return repo

    @staticmethod
    def clone(path_to_repo: Path, repo_to_clone: "GitRepository"):
        assert_has_git()
        path_to_repo.parent.mkdir(parents=True, exist_ok=True)
        cloned_repo = GitRepository(path_to_repo)
        cloned_repo.clone(repo_to_clone.path_to_repo)
        return cloned_repo

    @staticmethod
    def load_existing_repo(path_to_repo: Path):
        assert_has_git()
        path = GitRepository.get_repo_root(path_to_repo)
        return GitRepository(path)


class GitRepository:
    def __init__(self, path_to_repo: Path):
        """
        This class should not be instantiated directly, use `Git.init/clone/from_existing` instead.
        """
        self.path_to_repo = path_to_repo.resolve()

    @staticmethod
    def get_repo_root(path_to_repo: Path):
        credentials = [] if has_git_credentials() else DEFAULT_CREDENTIALS
        process = subprocess.run(
            ["git", *credentials, "rev-parse", "--show-toplevel"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            cwd=path_to_repo,
            check=False,
        )

        if process.returncode:
            raise InvalidGitRepositoryException(
                f"{path_to_repo} is not a valid git repository."
            )

        path = Path(process.stdout.decode("utf-8").strip())
        return path.resolve()

    @wrap_git_exception
    def init(self):
        credentials = [] if has_git_credentials() else DEFAULT_CREDENTIALS
        subprocess.run(
            ["git", *credentials, "init"],
            **SHARED_KWARGS,
            cwd=self.path_to_repo,
        )

    @wrap_git_exception
    def clone(self, path_to_repo_to_clone: Path):
        credentials = [] if has_git_credentials() else DEFAULT_CREDENTIALS
        subprocess.run(
            [
                "git",
                *credentials,
                "clone",
                path_to_repo_to_clone,
                self.path_to_repo.name,
            ],
            **SHARED_KWARGS,
            cwd=self.path_to_repo.parent,
        )

    @wrap_git_exception
    def add_submodule(
        self,
        url: str,
        path_to_submodule: Path,
        name: str,
        branch: Optional[str] = None,
        depth: int = 1,
    ):
        credentials = [] if has_git_credentials() else DEFAULT_CREDENTIALS
        subprocess.run(
            ["git", *credentials, "submodule", "add"]
            + (["-b", branch] if branch else [])  # (tag)
            + [
                "--name",
                name,
                "--depth",
                str(depth),
                url,
                str(path_to_submodule.relative_to(self.path_to_repo)),
            ],
            **SHARED_KWARGS,
            cwd=self.path_to_repo,
        )

    @wrap_git_exception
    def update_submodule(self, path_to_submodule: Path, init=False):
        credentials = [] if has_git_credentials() else DEFAULT_CREDENTIALS
        subprocess.run(
            ["git", *credentials, "submodule", "update"]
            + (["--init"] if init else [])
            + [str(path_to_submodule)],
            **SHARED_KWARGS,
            cwd=self.path_to_repo,
        )

    @wrap_git_exception
    def add(self, path_to_item: Path):
        credentials = [] if has_git_credentials() else DEFAULT_CREDENTIALS
        subprocess.run(
            [
                "git",
                *credentials,
                "add",
                str(path_to_item),
            ],
            **SHARED_KWARGS,
            cwd=self.path_to_repo,
        )

    @wrap_git_exception
    def remove_submodule(self, path_to_submodule: Path):
        credentials = [] if has_git_credentials() else DEFAULT_CREDENTIALS
        subprocess.run(
            [
                "git",
                *credentials,
                "rm",
                "--force",
                str(path_to_submodule),
            ],
            **SHARED_KWARGS,
            cwd=self.path_to_repo,
        )

    @wrap_git_exception
    def commit(self, msg: str):
        credentials = [] if has_git_credentials() else DEFAULT_CREDENTIALS
        subprocess.run(
            ["git", *credentials, "commit", "-m", msg],
            **SHARED_KWARGS,
            cwd=self.path_to_repo,
        )

    def get_submodules(self) -> Dict[str, PackageInfo]:
        """
        Returns a dictionary of form:
        submodule_name: PackageInfo
        """

        gitmodules_path = self.path_to_repo / ".gitmodules"
        if os.path.isfile(gitmodules_path):

            with open(gitmodules_path, "r", encoding="utf-8") as file:
                data = file.read()
                names = re.finditer(r"\[submodule \"([^\"]+)\"\]", data)
                paths = re.finditer(r"path = (.+)\n", data)
                urls = re.finditer(r"url = (.+)\n", data)
                return {
                    name[1]: PackageInfo(
                        name=name[1],
                        url=url[1],
                        path=Path(path[1]),
                    )
                    for name, path, url in zip(names, paths, urls)
                }
        return {}


def assert_has_git():
    try:
        subprocess.run(["git", "--version"], **SHARED_KWARGS)
    except subprocess.CalledProcessError as ex:
        raise GitNotFoundException("Git executable not found.") from ex


def has_git_credentials():
    try:
        subprocess.run(["git", "config", "user.name"], **SHARED_KWARGS)
    except subprocess.CalledProcessError:
        return False
    return True
