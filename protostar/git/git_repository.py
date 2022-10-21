import os.path
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from protostar.git.git_exceptions import (
    InvalidGitRepositoryException,
    wrap_git_exception,
)


@dataclass
class Submodule:
    name: str
    url: str
    version: Optional[str] = None
    path: Optional[Path] = None


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
        tag: Optional[str] = None,
        depth: int = 1,
    ):
        credentials = [] if has_git_credentials() else DEFAULT_CREDENTIALS

        try:
            relative_submodule_path = submodule_path.relative_to(self.repo_path)
        except ValueError:
            relative_submodule_path = submodule_path

        subprocess.run(
            [
                "git",
                *credentials,
                "submodule",
                "add",
                "--name",
                name,
                "--depth",
                str(depth),
                "--force",
                url,
                str(relative_submodule_path),
            ],
            **SHARED_KWARGS,
            cwd=self.repo_path,
        )

        if tag:
            submodule_repo = GitRepository(self.repo_path / relative_submodule_path)
            submodule_repo.fetch_tags()
            submodule_repo.checkout(tag)

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
    def checkout(self, branch: str):
        subprocess.run(["git", "checkout", branch], **SHARED_KWARGS, cwd=self.repo_path)

    @wrap_git_exception
    def create_tag(self, name: str):
        credentials = [] if has_git_credentials() else DEFAULT_CREDENTIALS
        subprocess.run(
            ["git", *credentials, "tag", name], **SHARED_KWARGS, cwd=self.repo_path
        )

    @wrap_git_exception
    def get_tag_rev(self) -> str:
        process = subprocess.run(
            ["git", "rev-list", "--tags", "--max-count=1"],
            stderr=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            check=True,
            cwd=self.repo_path,
        )
        return process.stdout.decode("utf-8").strip()

    @wrap_git_exception
    def get_tag(self, rev: Optional[str] = None) -> str:
        process = subprocess.run(
            ["git", "describe", "--tags"] + ([rev] if rev else []),
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

    @wrap_git_exception
    def fetch_tags(self):
        credentials = [] if has_git_credentials() else DEFAULT_CREDENTIALS
        subprocess.run(
            ["git", *credentials, "fetch", "--tags"],
            **SHARED_KWARGS,
            cwd=self.repo_path,
        )

    def get_submodules(self) -> Dict[str, Submodule]:
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
                    name[1]: Submodule(
                        name=name[1],
                        url=url[1],
                        path=Path(path[1]),
                    )
                    for name, path, url in zip(names, paths, urls)
                }
        return {}


@wrap_git_exception
def has_git_credentials():
    try:
        subprocess.run(["git", "config", "user.name"], **SHARED_KWARGS)
    except subprocess.CalledProcessError:
        return False
    return True
