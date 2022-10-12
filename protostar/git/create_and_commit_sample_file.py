from pathlib import Path

from protostar.git import GitRepository


def create_and_commit_sample_file(repo: GitRepository, directory: Path):
    with open(directory / "foo.txt", "w", encoding="utf-8") as some_file:
        some_file.write("foo")
        some_file.close()
    repo.add(directory)
    repo.commit("add foo.txt")
