from abc import ABC, abstractmethod
from typing import Optional, Type, TypeVar, Union

from .hint_local import HintLocal


class ExceptionMetadata(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def format(self) -> str:
        ...


MetadataT = TypeVar("MetadataT", bound=ExceptionMetadata)


class ReportedException(BaseException):
    """
    The exception used for catching unexpected errors thrown from test cases and as a base class.

    Contract:
        It is illegal to attach many same-type instances of ExceptionMetadata to the same exception
        object.
    """

    def __init__(self, *args: object) -> None:
        self.metadata: list[ExceptionMetadata] = []
        self.execution_info: dict[str, Union[int, str]] = {}
        super().__init__(*args)

    def __str__(self) -> str:
        return str(super().__repr__())

    def __getstate__(self):
        return self.__dict__.copy()

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.__dict__ == other.__dict__

    def get_metadata_by_type(
        self, metadata_type: Type[MetadataT]
    ) -> Optional[MetadataT]:
        for metadata in self.metadata:
            if isinstance(metadata, metadata_type):
                return metadata

        return None


class SimpleReportedException(ReportedException):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return str(self.message)


class BreakingReportedException(ReportedException):
    pass


class SimpleBreakingReportedException(
    SimpleReportedException, BreakingReportedException
):
    pass


CheatcodeNameProvider = Union[str, HintLocal]


class CheatcodeException(BreakingReportedException):
    def __init__(self, cheatcode: CheatcodeNameProvider, message: str):
        if isinstance(cheatcode, HintLocal):
            self.cheatcode_name = cheatcode.name
        else:
            self.cheatcode_name = cheatcode

        self.message = message
        super().__init__(message)

    def __str__(self):
        lines: list[str] = []
        lines.append(f"Incorrect usage of `{self.cheatcode_name}` cheatcode")
        lines.append(self.message)
        return "\n".join(lines)

    def __reduce__(self):
        return type(self), (self.cheatcode_name, self.message), self.__getstate__()


class KeywordOnlyArgumentCheatcodeException(CheatcodeException):
    def __init__(self, cheatcode: CheatcodeNameProvider, list_of_kwargs: list[str]):
        self.kwargs = list_of_kwargs
        super().__init__(cheatcode, "Passed keyword-only argument positionally.")

    def __str__(self):
        lines: list[str] = []
        lines.append(f"Incorrect usage of `{self.cheatcode_name}` cheatcode")
        lines.append(self.message)
        lines.append("Available kwargs:")
        lines.extend(f"`{kwarg}`" for kwarg in self.kwargs)
        return "\n".join(lines)
