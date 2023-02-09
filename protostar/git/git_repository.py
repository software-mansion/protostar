import os.path
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from typing_extensions import Self

from protostar.git.git import ensure_user_has_git, run_git
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
    @classmethod
    def create(cls, repo_path: Path):
        ensure_user_has_git()
        repo_path.mkdir(parents=True, exist_ok=True)
        repo = GitRepository(repo_path)
        repo.init()
        return repo

    @staticmethod
    def from_path(repo_path: Path):
        ensure_user_has_git()
        path = GitRepository.get_repo_root(repo_path)
        return GitRepository(path)

    @staticmethod
    def get_repo_root(repo_path: Path) -> Path:
        try:
            path_str = run_git(["rev-parse", "--show-toplevel"], cwd=repo_path)
        except ProtostarGitException as ex:
            raise InvalidGitRepositoryException(
                f"{repo_path} is not a valid git repository."
            ) from ex
        return Path(path_str).resolve()

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path.resolve()

    def init(self):
        self._git(["init"])

    def clone(self, new_repo_path: Path) -> Self:
        new_repo_path.parent.mkdir(parents=True, exist_ok=True)
        self._git(["clone", str(self.repo_path), str(new_repo_path)])
        return GitRepository(new_repo_path)

    def add_submodule(
        self,
        url: str,
        submodule_path: Path,
        name: str,
        tag: Optional[str] = None,
        depth: int = 1,
    ) -> None:
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
        return run_git(args=args, cwd=self.repo_path)

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
