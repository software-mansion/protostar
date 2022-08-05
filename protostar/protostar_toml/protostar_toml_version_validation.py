from protostar.protostar_exception import ProtostarException
from protostar.protostar_toml.io.protostar_toml_reader import ProtostarTOMLReader
from protostar.utils import VersionManager


def check_protostar_toml_compatibility(
    command: str,
    protostar_toml_reader: ProtostarTOMLReader,
    version_manager: VersionManager,
):
    if command in ["init", "upgrade"]:
        return

    declared_version_str = protostar_toml_reader.get_attribute(
        "config", "protostar_version"
    )

    # Version from protostar.toml
    declared_version = VersionManager.parse(declared_version_str)

    # Version from pyproject.toml
    last_supported_protostar_toml_version = (
        version_manager.last_supported_protostar_toml_version
    )

    if last_supported_protostar_toml_version > declared_version:
        raise ProtostarException(
            f"Protostar v{version_manager.protostar_version} is not compatible with provided protostar.toml.\n"
            "Please refer to https://github.com/software-mansion/protostar/releases, "
            "in order to convert protostar.toml to a newer version."
        )
