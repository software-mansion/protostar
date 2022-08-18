from contextlib import AbstractContextManager
from os import listdir, rmdir
from pathlib import Path
from typing import Union

from protostar.protostar_exception import ProtostarException


class MaybeTmpDirectory(AbstractContextManager):
    def __init__(self, path: Path):
        self._path = path

    def __enter__(self) -> None:
        self._create_dir()

    def _create_dir(self):
        if self._path.exists():
            raise DirectoryExistsException(self._path)
        self._path.mkdir()

    def __exit__(self, __exc_type, __exc_value, __traceback) -> Union[bool, None]:
        if self._is_directory_empty():
            rmdir(self._path)

    def _is_directory_empty(self) -> bool:
        return len(listdir(self._path)) == 0


class DirectoryExistsException(ProtostarException):
    def __init__(self, dir_path: Path) -> None:
        super().__init__(
            (
                f"Directory ({dir_path}) exists.\n"
                "Please delete, rename or relocate the directory."
            )
        )
