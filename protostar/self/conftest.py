from .protostar_compatibility_with_project_checker import (
    CompatibilityCheckOutput,
    DeclaredProtostarVersionProviderProtocol,
    ProtostarCompatibilityWithProjectCheckerProtocol,
    parse_protostar_version,
)


class FakeDeclaredProtostarVersionProvider(DeclaredProtostarVersionProviderProtocol):
    def __init__(self, declared_protostar_version_str: str):
        self._declared_protostar_version_str = declared_protostar_version_str

    def get_declared_protostar_version(self):
        return parse_protostar_version(self._declared_protostar_version_str)


class FakeProtostarCompatibilityWithProjectChecker(
    ProtostarCompatibilityWithProjectCheckerProtocol
):
    def __init__(self, result: CompatibilityCheckOutput):
        self._result = result

    def check_compatibility(self) -> CompatibilityCheckOutput:
        return self._result
