from contextlib import contextmanager
from pathlib import Path

from protostar.protostar_exception import ProtostarException


@contextmanager
def create_maybe_tmp_directory(path: Path):
    if path.exists():
        raise DirectoryExistsException(path)

    try:
        path.mkdir()
        yield path
    finally:
        is_directory_empty = not any(path.iterdir())
        if is_directory_empty:
            path.rmdir()


class DirectoryExistsException(ProtostarException):
    def __init__(self, dir_path: Path) -> None:
        super().__init__(
            (
                f"Directory ({dir_path}) exists.\n"
                "Please delete, rename or relocate the directory."
            )
        )
