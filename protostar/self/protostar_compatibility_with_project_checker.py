from typing import Protocol

from protostar.utils.protostar_directory import VersionType


class DeclaredProtostarVersionProvider(Protocol):
    def get_declared_protostar_version(self) -> VersionType:
        ...


class ProtostarVersionProvider(Protocol):
    def get_protostar_version(self) -> VersionType:
        ...


class ProtostarCompatibilityWithProjectChecker:
    def __init__(
        self,
        protostar_version_provider: ProtostarVersionProvider,
        declared_protostar_version_provider: DeclaredProtostarVersionProvider,
    ) -> None:
        self._protostar_version_provider = protostar_version_provider
        self._declared_protostar_version_provider = declared_protostar_version_provider

    def check_backward_and_forward_compatibility(self) -> bool:
        return True
