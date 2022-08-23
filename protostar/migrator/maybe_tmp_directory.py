from contextlib import AbstractContextManager, contextmanager
from pathlib import Path
from typing import Union

from protostar.protostar_exception import ProtostarException


@contextmanager
def MaybeTmpDirectory(path: Path):
    if path.exists():
        raise DirectoryExistsException(path)

    path.mkdir()
    yield path

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
