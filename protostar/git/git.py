from asyncio.subprocess import DEVNULL
from os import PathLike
import subprocess
import re
import os.path
from typing import Dict, NamedTuple, Optional
from pathlib import Path
from dataclasses import dataclass


@dataclass
class PackageInfo:
    name: str
    url: str
    path: Path


# set to true when debugging
GIT_VERBOSE = True
OUTPUT_KWARGS = (
    {}
    if GIT_VERBOSE
    else {
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }
)

TEMP_CONFIG = [
    "-c",
    'user.name="Protostar"',
    "-c",
    'user.email="protostar@protostar.protostar"',
]


class Git:
    @staticmethod
    def init(path_to_repo: Path):
        path_to_repo.mkdir(parents=True, exist_ok=True)
        repo = GitRepository(path_to_repo)
        repo.init()
        return repo

    @staticmethod
    def clone(path_to_repo: Path, repo_to_clone: "GitRepository"):
        path_to_repo.parent.mkdir(parents=True, exist_ok=True)
        cloned_repo = GitRepository(path_to_repo)
        cloned_repo.clone(repo_to_clone.path_to_repo)
        return cloned_repo

    @staticmethod
    def from_existing(path_to_repo: Path):
        return GitRepository(path_to_repo)


class GitRepository:
    def __init__(self, path_to_repo: Path):
        """
        This class should not be instantiated directly, use `Git.init/clone/from_existing` instead.
        """
        self.path_to_repo = path_to_repo.resolve()

    def is_initialized(self):
        """
        Although Git.init works even if repo is already initialized,
        we use this to prevent the user from initializing repos accidentally.
        (i.e. with `protostar install` instead of `protostar init`)
        """
        return (
            subprocess.run(
                ["git", *TEMP_CONFIG, "status"],
                **OUTPUT_KWARGS,
                cwd=self.path_to_repo,
            ).returncode
            == 0
        )

    def init(self):
        subprocess.run(
            ["git", *TEMP_CONFIG, "init"],
            **OUTPUT_KWARGS,
            cwd=self.path_to_repo,
        )

    def clone(self, path_to_repo_to_clone: Path):
        subprocess.run(
            [
                "git",
                *TEMP_CONFIG,
                "clone",
                path_to_repo_to_clone,
                self.path_to_repo.name,
            ],
            **OUTPUT_KWARGS,
            cwd=self.path_to_repo.parent,
        )

    def add_submodule(
        self,
        url: str,
        path_to_submodule: Path,
        name: str,
        branch: Optional[str] = None,
        depth: int = 1,
    ):
        subprocess.run(
            ["git", *TEMP_CONFIG, "submodule", "add"]
            + (["-b", branch] if branch else [])  # (tag)
            + [
                "--name",
                name,
                "--depth",
                str(depth),
                url,
                str(path_to_submodule.relative_to(self.path_to_repo)),
            ],
            **OUTPUT_KWARGS,
            cwd=self.path_to_repo,
        )

    def update_submodule(self, path_to_submodule: Path, init=False):
        subprocess.run(
            ["git", *TEMP_CONFIG, "submodule", "update"]
            + (["--init"] if init else [])
            + [str(path_to_submodule)],
            **OUTPUT_KWARGS,
            cwd=self.path_to_repo,
        )

    def add(self, path_to_item: Path):
        subprocess.run(
            [
                "git",
                *TEMP_CONFIG,
                "add",
                str(path_to_item),
            ],
            **OUTPUT_KWARGS,
            cwd=self.path_to_repo,
        )

    def rm(self, path_to_item: Path, force: bool = False):
        subprocess.run(
            [
                "git",
                *TEMP_CONFIG,
                "rm",
            ]
            + (["--force"] if force else [])
            + [
                str(path_to_item),
            ],
            **OUTPUT_KWARGS,
            cwd=self.path_to_repo,
        )

    def commit(self, msg: str):
        subprocess.run(
            ["git", *TEMP_CONFIG, "commit", "-m", msg],
            **OUTPUT_KWARGS,
            cwd=self.path_to_repo,
        )

    def get_submodules(self) -> Dict[str, PackageInfo]:
        """
        Returns a dictionary of form:
        submodule_name: PackageData(url=submodule_url, path=submodule_path)
        """

        gitmodules_path = self.path_to_repo / ".gitmodules"
        if os.path.isfile(gitmodules_path):

            with open(gitmodules_path, "r") as file:
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
