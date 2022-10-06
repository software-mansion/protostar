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
    def clone(repo_path: Path, repo_to_clone: GitRepository):
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

    @staticmethod
    @wrap_git_exception
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
        except FileNotFoundError as ex:
            raise GitNotFoundException("Git executable not found.") from ex
