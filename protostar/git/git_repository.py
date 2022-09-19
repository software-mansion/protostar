from asyncio.subprocess import DEVNULL
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
VERBOSE = True
STDOUT_STREAM = subprocess.PIPE if VERBOSE else subprocess.DEVNULL
STDERR_STREAM = subprocess.STDOUT if VERBOSE else subprocess.DEVNULL


class GitRepository:
    def __init__(self, path_to_repo: Path):
        self.path_to_repo = path_to_repo.resolve()
        self.path_to_repo.mkdir(parents=True, exist_ok=True)

    # @classmethod
    # def clone(cls, repo_to_clone: str):

    def is_initialized(self):
        return (
            subprocess.run(
                ["cd", str(self.path_to_repo), "&&", "git", "status"],
                stdout=STDOUT_STREAM,
                stderr=STDERR_STREAM,
            ).returncode
            == 0
        )

    def init(self):
        subprocess.run(
            ["cd", str(self.path_to_repo), "&&", "git", "init"],
            stdout=STDOUT_STREAM,
            stderr=STDERR_STREAM,
        )

    def clone(self, repo_to_clone: str):
        subprocess.run(
            ["cd", str(self.path_to_repo.parent), "&&", "git", "clone", repo_to_clone],
            stdout=STDOUT_STREAM,
            stderr=STDERR_STREAM,
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
            ["cd", str(self.path_to_repo), "&&", "git", "submodule", "add"]
            + (["-b", branch] if branch else [])  # (tag)
            + [
                "--name",
                name,
                "--depth",
                str(depth),
                url,
                str(path_to_submodule),
            ],
            stdout=STDOUT_STREAM,
            stderr=STDERR_STREAM,
        )

    def update_submodule(self, path_to_submodule: Path, init=False):
        subprocess.run(
            ["cd", str(self.path_to_repo), "&&", "git", "submodule", "update"]
            + (["--init"] if init else [])
            + [str(path_to_submodule)],
            stdout=STDOUT_STREAM,
            stderr=STDERR_STREAM,
        )

    def add(self, path_to_item: Path):
        subprocess.run(
            [
                "cd",
                str(self.path_to_repo),
                "&&",
                "git",
                "add",
                str(path_to_item.resolve()),
            ],
            stdout=STDOUT_STREAM,
            stderr=STDERR_STREAM,
        )

    def rm(self, path_to_item: Path):
        subprocess.run(
            [
                "cd",
                str(self.path_to_repo),
                "&&",
                "git",
                "rm",
                str(path_to_item.resolve()),
            ],
            stdout=STDOUT_STREAM,
            stderr=STDERR_STREAM,
        )

    def commit(self, msg: str):
        subprocess.run(
            ["cd", str(self.path_to_repo), "&&", "git", "commit", "-m", msg],
            stdout=STDOUT_STREAM,
            stderr=STDERR_STREAM,
        )

    def get_submodules(self) -> Dict[str, NamedTuple]:
        """
        Returns a dictionary of form:
        submodule_name: PackageData(url=submodule_url, path=submodule_path)
        """

        gitmodules_path = self.path_to_repo / ".gitmodules"
        if os.path.isfile(gitmodules_path):

            PackageData = NamedTuple("PackageData", [("url", str), ("path", Path)])

            with open(gitmodules_path, "r") as file:
                data = file.read()
                names = re.finditer(r"\[submodule \"([^\"]+)\"\]", data)
                paths = re.finditer(r"path = (.+)\n", data)
                urls = re.finditer(r"url = (.+)\n", data)
                return {
                    name[1]: PackageData(Path(url=url[1], path=path[1]))
                    for name, path, url in zip(names, paths, urls)
                }
        return {}
