from abc import ABC, abstractmethod
from dataclasses import dataclass

from starkware.cairo.lang.compiler.preprocessor.pass_manager import PassManager


@dataclass(frozen=True)
class PassManagerConfig:
    include_paths: list[str]
    disable_hint_validation: bool


class PassManagerFactory(ABC):
    @staticmethod
    @abstractmethod
    def build(config: PassManagerConfig) -> PassManager:
        ...
