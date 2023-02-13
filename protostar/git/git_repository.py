import os.path
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

from typing_extensions import Self

from .git_helpers import ensure_user_has_git, find_repo_root, run_git


@dataclass
class Submodule:
    name: str
    url: str
    version: Optional[str] = None
    path: Optional[Path] = None


@dataclass
class GitStatusResult:
    files_to_be_committed: list[Path]


class GitRepository:
    @classmethod
    def create(cls, repo_path: Path):
        ensure_user_has_git()
        repo_path.mkdir(parents=True, exist_ok=True)
        repo = GitRepository(repo_path)
        repo.init()
        return repo

    @classmethod
    def from_existing(cls, repo_path: Path):
        ensure_user_has_git()
        path = find_repo_root(repo_path)
        return cls(path)

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path.resolve()

    def init(self):
        self._git("init")

    def clone(self, new_repo_path: Path) -> Self:
        new_repo_path.parent.mkdir(parents=True, exist_ok=True)
        self._git("clone", str(self.repo_path), str(new_repo_path))
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
            "submodule",
            "add",
            "--name",
            name,
            "--depth",
            str(depth),
            "--force",
            url,
            str(relative_submodule_path),
        )
        if tag:
            submodule_repo = GitRepository(self.repo_path / relative_submodule_path)
            submodule_repo.fetch_tags()
            submodule_repo.checkout(tag)

    def update_submodule(self, submodule_path: Path) -> None:
        self._git("submodule", "update", "--init", str(submodule_path))

    def add(self, path_to_item: Path) -> None:
        self._git("add", str(path_to_item))

    def remove_submodule(self, submodule_path: Path) -> None:
        self._git("rm", "--force", str(submodule_path))

    def commit(self, msg: str) -> None:
        self._git("commit", "-m", msg)

    def checkout(self, branch: str) -> None:
        self._git("checkout", branch)

    def create_tag(self, name: str) -> None:
        self._git("tag", name)

    def get_tag_rev(self) -> str:
        return self._git("rev-list", "--tags", "--max-count=1")

    def get_tag(self, rev: Optional[str] = None) -> str:
        args = ["describe", "--tags"] + ([rev] if rev else [])
        return self._git(*args)

    def get_head(self) -> str:
        return self._git("rev-parse", "HEAD")

    def get_status(self) -> GitStatusResult:
        result = GitStatusResult(files_to_be_committed=[])
        output = self._git("status", "--porcelain")
        lines = output.splitlines()
        for line in lines:
            single_spaced_line = re.sub(" +", " ", line)
            segments = single_spaced_line.split()
            status = segments[0]
            file_path = segments[1]
            if status != "??":
                result.files_to_be_committed.append(Path(file_path))
        return result

    def fetch_tags(self):
        self._git("fetch", "--tags")

    def _git(self, *args: Union[str, Path]) -> str:
        return run_git(*args, cwd=self.repo_path)

    def get_submodules(self) -> dict[str, Submodule]:
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
