from protostar.protostar_exception import ProtostarException
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
        declared_version_str = self._protostar_toml_reader.get_attribute(
            "config", "protostar_version"
        )

        if not declared_version_str:
            raise ProtostarException(
                "Couldn't load `protostar_version`\n"
                "`protostar.toml` could've been created or modified by a newer version of Protostar".
                f"{REFER_TO}"
            )

        declared_version = VersionManager.parse(declared_version_str)

        # Version from pyproject.toml
        last_supported_protostar_toml_version = (
            self._version_manager.last_supported_protostar_toml_version
        )

        if not last_supported_protostar_toml_version:
            return

        if last_supported_protostar_toml_version > declared_version:
            raise ProtostarException(
                f"Protostar v{self._version_manager.protostar_version} "
                "is not compatible with provided protostar.toml.\n"
                f"{REFER_TO}"
            )
