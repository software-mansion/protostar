from protostar.protostar_toml.io.protostar_toml_reader import ProtostarTOMLReader
from protostar.utils import VersionManager


REFER_TO = (
    "Please refer to https://github.com/software-mansion/protostar/releases, "
    "in order to convert protostar.toml or upgrade protostar to a newer version."
)


class ProtostarTOMLVersionChecker:
    def __init__(
        self,
        protostar_toml_reader: ProtostarTOMLReader,
        version_manager: VersionManager,
    ):
        self._protostar_toml_reader = protostar_toml_reader
        self._version_manager = version_manager

    def run(self):
        # TODO: Implement
        pass
