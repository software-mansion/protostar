from abc import ABC, abstractmethod
from typing import Dict, List, Union


class ProtostarTOMLSection(ABC):
    TOMLCompatibleDict = Dict[str, Union[str, int, bool, List[str]]]

    @staticmethod
    @abstractmethod
    def get_section_name() -> str:
        ...

    @abstractmethod
    def to_dict(self) -> "ProtostarTOMLSection.TOMLCompatibleDict":
        ...
