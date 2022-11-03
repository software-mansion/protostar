import pytest

from .protostar_compatibility_with_project_checker import (
    CompatibilityCheckResult,
    DeclaredProtostarVersionProviderProtocol,
    ProtostarCompatibilityWithProjectChecker,
    parse_protostar_version,
)


class FakeDeclaredProtostarVersionProvider(DeclaredProtostarVersionProviderProtocol):
    def __init__(self, declared_protostar_version_str: str):
        self._declared_protostar_version_str = declared_protostar_version_str

    def get_declared_protostar_version(self):
        return parse_protostar_version(self._declared_protostar_version_str)


@pytest.fixture(name="declared_protostar_version_provider")
def declared_protostar_version_provider_fixture(declared_protostar_version: str):
    return FakeDeclaredProtostarVersionProvider(declared_protostar_version)


@pytest.mark.parametrize(
    "protostar_version, declared_protostar_version, is_compatible",
    (
        ("0.1.2", "0.1.2", CompatibilityCheckResult.COMPATIBLE),
        ("0.1.2", "0.1.1", CompatibilityCheckResult.COMPATIBLE),
        ("1.0.0", "1.0.0", CompatibilityCheckResult.COMPATIBLE),
        ("0.1.1", "0.1.2", CompatibilityCheckResult.OUTDATED_PROTOSTAR),
        ("1.0.0", "1.1.0", CompatibilityCheckResult.OUTDATED_PROTOSTAR),
        ("0.2.0", "0.1.2", CompatibilityCheckResult.OUTDATED_DECLARED_VERSION),
        ("1.0.0", "0.9.0", CompatibilityCheckResult.OUTDATED_DECLARED_VERSION),
    ),
)
def test_compatibility(
    declared_protostar_version_provider: DeclaredProtostarVersionProviderProtocol,
    protostar_version: str,
    is_compatible: bool,
):
    compatibility_checker = ProtostarCompatibilityWithProjectChecker(
        parse_protostar_version(protostar_version),
        declared_protostar_version_provider,
    )

    result = compatibility_checker.check_compatibility()

    assert result == is_compatible
