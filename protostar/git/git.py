import subprocess
from pathlib import Path
from .git_repository import GitRepository
from .git_exceptions import wrap_git_exception, GitNotFoundException


class Git:
    @staticmethod
    def init(repo_path: Path):
        Git.ensure_has_git()
        repo_path.mkdir(parents=True, exist_ok=True)
        repo = GitRepository(repo_path)
        repo.init()
        return repo

    @staticmethod
    def clone(repo_path: Path, repo_to_clone: "GitRepository"):
        Git.ensure_has_git()
        repo_path.parent.mkdir(parents=True, exist_ok=True)
        cloned_repo = GitRepository(repo_path)
        cloned_repo.clone(repo_to_clone.repo_path)
        return cloned_repo

    @staticmethod
    def load_existing_repo(repo_path: Path):
        Git.ensure_has_git()
        path = GitRepository.get_repo_root(repo_path)
        return GitRepository(path)

    @wrap_git_exception
    @staticmethod
    def get_version() -> str:
        Git.ensure_has_git()
        process = subprocess.run(
            ["git", "--version"],
            stderr=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            check=True,
        )
        return process.stdout.decode("utf-8").strip()

    @staticmethod
    def ensure_has_git():
        try:
            subprocess.run(
                ["git", "--version"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
<<<<<<< HEAD
        except FileNotFoundError as ex:
            raise GitNotFoundException("Git executable not found.") from ex
=======

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
>>>>>>> master
