import os.path
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from protostar.git.git_exceptions import (
    InvalidGitRepositoryException,
    ProtostarGitException,
)


@dataclass
class Submodule:
    name: str
    url: str
    version: Optional[str] = None
    path: Optional[Path] = None


class GitRepository:
    @staticmethod
    def get_repo_root(repo_path: Path) -> Path:
        try:
            path_str = git(["rev-parse", "--show-toplevel"], repo_path=repo_path)
        except ProtostarGitException as ex:
            raise InvalidGitRepositoryException(
                f"{repo_path} is not a valid git repository."
            ) from ex
        return Path(path_str).resolve()

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path.resolve()

    def init(self):
        self._git(["init"])

    def clone(self, repo_path_to_clone: Path):
        self._git(["clone", str(repo_path_to_clone), self.repo_path.name])

    def add_submodule(
        self,
        url: str,
        submodule_path: Path,
        name: str,
        tag: Optional[str] = None,
        depth: int = 1,
    ):
        try:
            relative_submodule_path = submodule_path.relative_to(self.repo_path)
        except ValueError:
            relative_submodule_path = submodule_path
        self._git(
            [
                "submodule",
                "add",
                "--name",
                name,
                "--depth",
                str(depth),
                "--force",
                url,
                str(relative_submodule_path),
            ]
        )
        if tag:
            submodule_repo = GitRepository(self.repo_path / relative_submodule_path)
            submodule_repo.fetch_tags()
            submodule_repo.checkout(tag)

    def update_submodule(self, submodule_path: Path) -> None:
        self._git(["submodule", "update", "--init", str(submodule_path)])

    def add(self, path_to_item: Path) -> None:
        self._git(["add", str(path_to_item)])

    def remove_submodule(self, submodule_path: Path) -> None:
        self._git(["rm", "--force", str(submodule_path)])

    def commit(self, msg: str) -> None:
        self._git(["commit", "-m", msg])

    def checkout(self, branch: str) -> None:
        self._git(["checkout", branch])

    def create_tag(self, name: str) -> None:
        self._git(["tag", name])

    def get_tag_rev(self) -> str:
        return self._git(["rev-list", "--tags", "--max-count=1"])

    def get_tag(self, rev: Optional[str] = None) -> str:
        return self._git(["describe", "--tags"] + ([rev] if rev else []))

    def get_head(self) -> str:
        return self._git(["rev-parse", "HEAD"])

    def fetch_tags(self):
        self._git(["fetch", "--tags"])

    def _git(self, args: list[str]) -> str:
        return git(args=args, repo_path=self.repo_path)

    def get_submodule_name_to_submodule(self) -> dict[str, Submodule]:
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


GIT_VERBOSE = False
SHARED_KWARGS = (
    {}
    if GIT_VERBOSE
    else {
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


def git(args: list[str], repo_path: Path):
    assert len(args) > 0
    assert args[0] != "git"
    credentials = [] if has_git_credentials() else DEFAULT_CREDENTIALS
    try:
        return (
            subprocess.run(
                ["git", *credentials, *args],
                check=True,
                cwd=repo_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            .stdout.decode("utf-8")
            .strip()
        )
    except subprocess.CalledProcessError as ex:
        raise ProtostarGitException(str(ex)) from ex


def has_git_credentials():
    try:
        subprocess.run(["git", "config", "user.name"], check=True, **SHARED_KWARGS)
    except subprocess.CalledProcessError:
        return False
    return True
