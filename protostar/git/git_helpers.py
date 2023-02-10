import subprocess
from pathlib import Path
from typing import Union

from .git_exceptions import (
    InvalidGitRepositoryException,
    ProtostarGitException,
    GitNotFoundException,
)

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


def run_git(*args: Union[str, Path], cwd: Path):
    assert len(args) > 0
    assert args[0] != "git"
    credentials = [] if has_user_git_credentials() else DEFAULT_CREDENTIALS
    str_args: list[str] = [str(arg) for arg in args]
    try:
        return (
            subprocess.run(
                ["git", *credentials, *str_args],
                check=True,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            .stdout.decode("utf-8")
            .strip()
        )
    except subprocess.CalledProcessError as ex:
        raise ProtostarGitException(str(ex)) from ex


def has_user_git_credentials():
    try:
        subprocess.run(["git", "config", "user.name"], check=True, **SHARED_KWARGS)
    except subprocess.CalledProcessError:
        return False
    return True


def get_git_version() -> str:
    ensure_user_has_git()
    process = subprocess.run(
        ["git", "--version"],
        stderr=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        check=True,
    )
    return process.stdout.decode("utf-8").strip()


def ensure_user_has_git():
    try:
        subprocess.run(
            ["git", "--version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError as ex:
        raise GitNotFoundException("Git executable not found.") from ex


def find_repo_root(repo_path: Path) -> Path:
    try:
        path_str = run_git("rev-parse", "--show-toplevel", cwd=repo_path)
    except ProtostarGitException as ex:
        raise InvalidGitRepositoryException(
            f"{repo_path} is not a valid git repository."
        ) from ex
    return Path(path_str).resolve()
