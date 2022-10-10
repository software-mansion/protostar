from abc import abstractmethod
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
