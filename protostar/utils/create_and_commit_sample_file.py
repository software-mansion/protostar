from pathlib import Path

from git.repo import Repo


def create_and_commit_sample_file(repo: Repo, directory: Path):
    with open(directory / "foo.txt", "w", encoding="utf-8") as some_file:
        some_file.write("foo")
        some_file.close()
    repo.git.add("-u")
    repo.index.commit("add foo.txt")
