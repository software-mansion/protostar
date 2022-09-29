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
    def init(repo_path: Path):
        ensure_has_git()
        repo_path.mkdir(parents=True, exist_ok=True)
        repo = GitRepository(repo_path)
        repo.init()
        return repo

    @staticmethod
    def clone(repo_path: Path, repo_to_clone: "GitRepository"):
        ensure_has_git()
        repo_path.parent.mkdir(parents=True, exist_ok=True)
        cloned_repo = GitRepository(repo_path)
        cloned_repo.clone(repo_to_clone.repo_path)
        return cloned_repo

    @staticmethod
    def load_existing_repo(repo_path: Path):
        ensure_has_git()
        path = GitRepository.get_repo_root(repo_path)
        return GitRepository(path)


class GitRepository:
    def __init__(self, repo_path: Path):
        """
        This class should not be instantiated directly, use `Git.init/clone/from_existing` instead.
        """
        self.repo_path = repo_path.resolve()

    @staticmethod
    def get_repo_root(repo_path: Path):
        credentials = [] if has_git_credentials() else DEFAULT_CREDENTIALS
        process = subprocess.run(
            ["git", *credentials, "rev-parse", "--show-toplevel"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            cwd=repo_path,
            check=False,
        )

        if process.returncode:
            raise InvalidGitRepositoryException(
                f"{repo_path} is not a valid git repository."
            )

        path = Path(process.stdout.decode("utf-8").strip())
        return path.resolve()

    @wrap_git_exception
    def init(self):
        credentials = [] if has_git_credentials() else DEFAULT_CREDENTIALS
        subprocess.run(
            ["git", *credentials, "init"],
            **SHARED_KWARGS,
            cwd=self.repo_path,
        )

    @wrap_git_exception
    def clone(self, repo_path_to_clone: Path):
        credentials = [] if has_git_credentials() else DEFAULT_CREDENTIALS
        subprocess.run(
            [
                "git",
                *credentials,
                "clone",
                repo_path_to_clone,
                self.repo_path.name,
            ],
            **SHARED_KWARGS,
            cwd=self.repo_path.parent,
        )

    @wrap_git_exception
    def add_submodule(
        self,
        url: str,
        submodule_path: Path,
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
                str(submodule_path.relative_to(self.repo_path)),
            ],
            **SHARED_KWARGS,
            cwd=self.repo_path,
        )

    @wrap_git_exception
    def update_submodule(self, submodule_path: Path):
        credentials = [] if has_git_credentials() else DEFAULT_CREDENTIALS
        subprocess.run(
            ["git", *credentials, "submodule", "update", "--init", str(submodule_path)],
            **SHARED_KWARGS,
            cwd=self.repo_path,
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
            cwd=self.repo_path,
        )

    @wrap_git_exception
    def remove_submodule(self, submodule_path: Path):
        credentials = [] if has_git_credentials() else DEFAULT_CREDENTIALS
        subprocess.run(
            [
                "git",
                *credentials,
                "rm",
                "--force",
                str(submodule_path),
            ],
            **SHARED_KWARGS,
            cwd=self.repo_path,
        )

    @wrap_git_exception
    def commit(self, msg: str):
        credentials = [] if has_git_credentials() else DEFAULT_CREDENTIALS
        subprocess.run(
            ["git", *credentials, "commit", "-m", msg],
            **SHARED_KWARGS,
            cwd=self.repo_path,
        )

    @wrap_git_exception
    def create_tag(self, name: str):
        credentials = [] if has_git_credentials() else DEFAULT_CREDENTIALS
        subprocess.run(
            ["git", *credentials, "tag", name], **SHARED_KWARGS, cwd=self.repo_path
        )

    @wrap_git_exception
    def get_current_tag(self) -> str:
        process = subprocess.run(
            ["git", "describe", "--tags"],
            stderr=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            check=True,
            cwd=self.repo_path,
        )
        return process.stdout.decode("utf-8").strip()

    @wrap_git_exception
    def get_head(self) -> str:
        process = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            check=True,
            cwd=self.repo_path,
        )
        return process.stdout.decode("utf-8").strip()

    def get_submodules(self) -> Dict[str, PackageInfo]:
        """
        Returns a dictionary of form:
        submodule_name: PackageInfo
        """

        gitmodules_path = self.repo_path / ".gitmodules"
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


def ensure_has_git():
    try:
        subprocess.run(["git", "--version"], **SHARED_KWARGS)
    except FileNotFoundError as ex:
        raise GitNotFoundException("Git executable not found.") from ex


def has_git_credentials():
    try:
        subprocess.run(["git", "config", "user.name"], **SHARED_KWARGS)
    except subprocess.CalledProcessError:
        return False
    return True
