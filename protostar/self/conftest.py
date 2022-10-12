from .protostar_compatibility_with_project_checker import (
    ProtostarVersionProviderProtocol,
    parse_protostar_version,
)


class FakeProtostarVersionProvider(ProtostarVersionProviderProtocol):
    def __init__(self, protostar_version_str: str):
        self._protostar_version_str = protostar_version_str

    def get_protostar_version(self):
        return parse_protostar_version(self._protostar_version_str)
