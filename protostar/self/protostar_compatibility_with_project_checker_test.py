import pytest

from protostar.utils import VersionManager

from .protostar_compatibility_with_project_checker import (
    DeclaredProtostarVersionProvider,
    ProtostarCompatibilityWithProjectChecker,
    ProtostarVersionProvider,
)


class DeclaredProtostarVersionProviderDouble(DeclaredProtostarVersionProvider):
    def __init__(self, declared_protostar_version_str: str):
        self._declared_protostar_version_str = declared_protostar_version_str

    def get_declared_protostar_version(self):
        return VersionManager.parse(self._declared_protostar_version_str)


class ProtostarVersionProviderDouble(ProtostarVersionProvider):
    def __init__(self, protostar_version_str: str):
        self._protostar_version_str = protostar_version_str

    def get_protostar_version(self):
        return VersionManager.parse(self._protostar_version_str)


@pytest.fixture(name="declared_protostar_version")
def declared_protostar_version_fixture() -> str:
    assert False, "Not parametrized"


@pytest.fixture(name="declared_protostar_version_provider")
def declared_protostar_version_provider_fixture(declared_protostar_version: str):
    return DeclaredProtostarVersionProviderDouble(declared_protostar_version)


@pytest.fixture(name="protostar_version")
def protostar_version_fixture() -> str:
    assert False, "Not parametrized"


@pytest.fixture(name="protostar_version_provider")
def protostar_version_provider_fixture(protostar_version: str):
    return ProtostarVersionProviderDouble(protostar_version)


@pytest.mark.parametrize(
    "protostar_version, declared_protostar_version",
    (
        ("0.1.2", "0.1.2"),
        ("0.1.2", "0.1.1"),
    ),
)
def test_compatibility(
    declared_protostar_version_provider: DeclaredProtostarVersionProvider,
    protostar_version_provider: ProtostarVersionProvider,
):
    compatibility_checker = ProtostarCompatibilityWithProjectChecker(
        protostar_version_provider,
        declared_protostar_version_provider,
    )

    is_compatible = compatibility_checker.check_backward_and_forward_compatibility()

    assert is_compatible
