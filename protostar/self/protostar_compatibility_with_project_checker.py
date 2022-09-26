from enum import Enum, auto
from typing import Optional, Protocol

from packaging import version

ProtostarVersion = version.Version


class DeclaredProtostarVersionProviderProtocol(Protocol):
    def get_declared_protostar_version(self) -> Optional[ProtostarVersion]:
        ...


class ProtostarVersionProviderProtocol(Protocol):
    def get_protostar_version(self) -> ProtostarVersion:
        ...


class CompatibilityCheckResult(Enum):
    COMPATIBLE = auto()
    OUTDATED_PROTOSTAR = auto()
    OUTDATED_DECLARED_VERSION = auto()
    FAILURE = auto()


class ProtostarCompatibilityWithProjectChecker:
    def __init__(
        self,
        protostar_version_provider: ProtostarVersionProviderProtocol,
        declared_protostar_version_provider: DeclaredProtostarVersionProviderProtocol,
    ) -> None:
        self._protostar_version_provider = protostar_version_provider
        self._declared_protostar_version_provider = declared_protostar_version_provider

    def check_compatibility(self) -> CompatibilityCheckResult:
        protostar_version = self._protostar_version_provider.get_protostar_version()
        declared_protostar_version = (
            self._declared_protostar_version_provider.get_declared_protostar_version()
        )
        if declared_protostar_version is None:
            return CompatibilityCheckResult.FAILURE
        if (
            declared_protostar_version.major == protostar_version.major
            and declared_protostar_version.minor == protostar_version.minor
            and declared_protostar_version.micro <= protostar_version.micro
        ):
            return CompatibilityCheckResult.COMPATIBLE
        if declared_protostar_version < protostar_version:
            return CompatibilityCheckResult.OUTDATED_DECLARED_VERSION
        return CompatibilityCheckResult.OUTDATED_PROTOSTAR


def parse_protostar_version(value: str) -> ProtostarVersion:
    result = version.parse(value)
    assert isinstance(result, ProtostarVersion)
    return result
