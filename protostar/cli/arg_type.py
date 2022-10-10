import re
from abc import abstractmethod
from pathlib import Path
from re import Pattern
from typing import Generic, TypeVar

ParsingResultT = TypeVar("ParsingResultT")


class ArgType(Generic[ParsingResultT]):
    @abstractmethod
    def get_name(self) -> str:
        ...

    @abstractmethod
    def parse(self, arg: str) -> ParsingResultT:
        ...


class StringArgType(ArgType[str]):
    def get_name(self):
        return "str"

    def parse(self, arg: str) -> str:
        return arg


class DirectoryArgType(ArgType[Path]):
    def get_name(self):
        return "directory"

    def parse(self, arg: str) -> Path:
        path = Path(arg)
        assert path.is_dir(), f'"{str(path)}" is not a valid directory path'
        return path


class PathArgType(ArgType[Path]):
    def get_name(self) -> str:
        return "path"

    def parse(self, arg: str) -> Path:
        return Path(arg)


class RegexArgType(ArgType[Pattern]):
    def get_name(self) -> str:
        return "regex"

    def parse(self, arg: str) -> Pattern:
        return re.compile(arg)
