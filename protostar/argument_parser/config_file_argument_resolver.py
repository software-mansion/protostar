from typing import Any, Optional, Protocol


class ConfigFileArgumentResolverProtocol(Protocol):
    def resolve_argument(
        self, command_name: Optional[str], argument_name: str
    ) -> Optional[Any]:
        ...
