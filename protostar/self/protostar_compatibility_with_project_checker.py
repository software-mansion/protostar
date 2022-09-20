from enum import Enum, auto
from typing import Protocol

from packaging.version import Version


class DeclaredProtostarVersionProvider(Protocol):
    def get_declared_protostar_version(self) -> Version:
        ...


class ProtostarVersionProvider(Protocol):
    def get_protostar_version(self) -> Version:
        ...


class CompatibilityCheckResult(Enum):
    COMPATIBLE = auto()
    OUTDATED_PROTOSTAR = auto()
    OUTDATED_DECLARED_VERSION = auto()


class ProtostarCompatibilityWithProjectChecker:
    def __init__(
        self,
        protostar_version_provider: ProtostarVersionProvider,
        declared_protostar_version_provider: DeclaredProtostarVersionProvider,
    ) -> None:
        self._protostar_version_provider = protostar_version_provider
        self._declared_protostar_version_provider = declared_protostar_version_provider

    def check_compatibility(self) -> CompatibilityCheckResult:
        protostar_version = self._protostar_version_provider.get_protostar_version()
        declared_protostar_version = (
            self._declared_protostar_version_provider.get_declared_protostar_version()
        )
        if (
            declared_protostar_version.major == protostar_version.major
            and declared_protostar_version.minor == protostar_version.minor
            and declared_protostar_version.micro <= protostar_version.micro
        ):
            return CompatibilityCheckResult.COMPATIBLE
        if declared_protostar_version < protostar_version:
            return CompatibilityCheckResult.OUTDATED_DECLARED_VERSION
        return CompatibilityCheckResult.OUTDATED_PROTOSTAR
