from enum import Enum, auto
from typing import Optional, Protocol

from packaging import version

ProtostarVersion = version.Version


class DeclaredProtostarVersionProviderProtocol(Protocol):
    def get_declared_protostar_version(self) -> Optional[ProtostarVersion]:
        ...


class CompatibilityCheckResult(Enum):
    COMPATIBLE = auto()
    OUTDATED_PROTOSTAR = auto()
    OUTDATED_DECLARED_VERSION = auto()
    FAILURE = auto()


class ProtostarCompatibilityWithProjectCheckerProtocol(Protocol):
    def check_compatibility(self) -> CompatibilityCheckResult:
        ...


class ProtostarCompatibilityWithProjectChecker(
    ProtostarCompatibilityWithProjectCheckerProtocol
):
    def __init__(
        self,
        protostar_version: ProtostarVersion,
        declared_protostar_version_provider: DeclaredProtostarVersionProviderProtocol,
    ) -> None:
        self._protostar_version = protostar_version
        self._declared_protostar_version_provider = declared_protostar_version_provider

    def check_compatibility(self) -> CompatibilityCheckResult:

        declared_protostar_version = (
            self._declared_protostar_version_provider.get_declared_protostar_version()
        )
        if (
            declared_protostar_version is None
            or self._protostar_version.major == 0
            and self._protostar_version.minor == 0
            and self._protostar_version.micro == 0
        ):
            return CompatibilityCheckResult.FAILURE
        if (
            declared_protostar_version.major == self._protostar_version.major
            and declared_protostar_version.minor == self._protostar_version.minor
            and declared_protostar_version.micro <= self._protostar_version.micro
        ):
            return CompatibilityCheckResult.COMPATIBLE
        if declared_protostar_version < self._protostar_version:
            return CompatibilityCheckResult.OUTDATED_DECLARED_VERSION
        return CompatibilityCheckResult.OUTDATED_PROTOSTAR


def parse_protostar_version(value: str) -> ProtostarVersion:
    result = version.parse(value)
    assert isinstance(result, ProtostarVersion)
    return result
