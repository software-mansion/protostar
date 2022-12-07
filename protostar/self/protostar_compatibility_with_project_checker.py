from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Protocol

from packaging import version

ProtostarVersion = version.Version


class DeclaredProtostarVersionProviderProtocol(Protocol):
    def get_declared_protostar_version(self) -> Optional[ProtostarVersion]:
        ...


class CompatibilityResult(Enum):
    COMPATIBLE = auto()
    OUTDATED_PROTOSTAR = auto()
    OUTDATED_DECLARED_VERSION = auto()
    FAILURE = auto()


@dataclass
class CompatibilityCheckOutput:
    compatibility_result: CompatibilityResult
    protostar_version_str: str
    declared_protostar_version_str: Optional[str]


class ProtostarCompatibilityWithProjectCheckerProtocol(Protocol):
    def check_compatibility(self) -> CompatibilityCheckOutput:
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

    def check_compatibility(self) -> CompatibilityCheckOutput:
        declared_protostar_version = (
            self._declared_protostar_version_provider.get_declared_protostar_version()
        )
        return CompatibilityCheckOutput(
            compatibility_result=self._check_compatibility(declared_protostar_version),
            declared_protostar_version_str=str(declared_protostar_version)
            if declared_protostar_version is not None
            else None,
            protostar_version_str=str(self._protostar_version),
        )

    def _check_compatibility(
        self, declared_protostar_version: Optional[ProtostarVersion]
    ) -> CompatibilityResult:
        if (
            declared_protostar_version is None
            or self._protostar_version.major == 0
            and self._protostar_version.minor == 0
            and self._protostar_version.micro == 0
        ):
            return CompatibilityResult.FAILURE
        if (
            declared_protostar_version.major == self._protostar_version.major
            and declared_protostar_version.minor == self._protostar_version.minor
            and declared_protostar_version.micro <= self._protostar_version.micro
        ):
            return CompatibilityResult.COMPATIBLE
        if declared_protostar_version < self._protostar_version:
            return CompatibilityResult.OUTDATED_DECLARED_VERSION
        return CompatibilityResult.OUTDATED_PROTOSTAR


def parse_protostar_version(value: str) -> ProtostarVersion:
    result = version.parse(value)
    assert isinstance(result, ProtostarVersion)
    return result
