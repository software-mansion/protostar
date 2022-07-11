from abc import ABC, abstractmethod
from typing import Dict, List, Union


class MigrationResultJSON:
    class Log(ABC):
        ResultType = Dict[str, Union[str, int]]

        @property
        @abstractmethod
        def operation_name(self) -> str:
            ...

        @property
        @abstractmethod
        def result(self) -> "ResultType":
            ...

    class Writer:
        def save(self, logs: List["MigrationResultJSON.Log"]):
            raise NotImplementedError()
