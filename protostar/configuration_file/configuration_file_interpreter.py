from abc import ABC, abstractmethod
from typing import Any, Optional


class ConfigurationFileInterpreter(ABC):
    @abstractmethod
    def get_section(
        self,
        section_name: str,
        profile_name: Optional[str] = None,
        section_namespace: Optional[str] = None,
    ) -> Optional[dict[str, Any]]:
        ...

    @abstractmethod
    def get_attribute(
        self,
        section_name: str,
        attribute_name: str,
        profile_name: Optional[str] = None,
        section_namespace: Optional[str] = None,
    ) -> Optional[Any]:
        ...

    @abstractmethod
    def get_profile_names(self) -> list[str]:
        ...
