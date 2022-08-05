from protostar.protostar_exception import ProtostarException
from protostar.protostar_toml.io.protostar_toml_reader import ProtostarTOMLReader
from protostar.utils import VersionManager


class ProtostarTOMLVersionChecker:
    def __init__(
        self,
        protostar_toml_reader: ProtostarTOMLReader,
        version_manager: VersionManager,
    ):
        self._protostar_toml_reader = protostar_toml_reader
        self._version_manager = version_manager

    def run(
        self,
        command: str,
    ):
        if command in ["init", "upgrade"]:
            return

        declared_version_str = self._protostar_toml_reader.get_attribute(
            "config", "protostar_version"
        )

        assert (
            declared_version_str
        ), "No protostar_version attribute available in protostar.toml"

        # Version from protostar.toml
        declared_version = VersionManager.parse(declared_version_str)

        # Version from pyproject.toml
        last_supported_protostar_toml_version = (
            self._version_manager.last_supported_protostar_toml_version
        )

        if last_supported_protostar_toml_version > declared_version:
            raise ProtostarException(
                f"Protostar v{self._version_manager.protostar_version} "
                "is not compatible with provided protostar.toml.\n"
                "Please refer to https://github.com/software-mansion/protostar/releases, "
                "in order to convert protostar.toml to a newer version."
            )
