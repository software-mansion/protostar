from pathlib import Path
from typing import Optional

from protostar.protostar_exception import ProtostarException

from .configuration_file import ConfigurationFile
from .configuration_file_v1 import ConfigurationFileV1
from .configuration_file_v2 import ConfigurationFileV2
from .configuration_legacy_toml_interpreter import ConfigurationLegacyTOMLInterpreter
from .configuration_toml_interpreter import ConfigurationTOMLInterpreter


class ConfigurationFileFactory:
    def __init__(self, cwd: Path) -> None:
        self._cwd = cwd

    def create(self) -> Optional[ConfigurationFile]:
        protostar_toml_path = self._search_upwards_protostar_toml_path()
        if protostar_toml_path is None:
            return None
        protostar_toml_content = protostar_toml_path.read_text()

        configuration_file_v2 = self._create_configuration_toml_v2(
            protostar_toml_path,
            protostar_toml_content,
        )
        if configuration_file_v2:
            return configuration_file_v2

        configuration_file_v1 = self._create_configuration_toml_v1(
            protostar_toml_path, protostar_toml_content
        )
        if configuration_file_v1:
            return configuration_file_v1

        raise ProtostarException(
            f"{protostar_toml_path} must specify `protostar-version` for example:\n"
            """
            [project]
            protostar-version = ?.?.?
            """,
        )

    def _create_configuration_toml_v2(
        self,
        protostar_toml_path: Path,
        protostar_toml_content: str,
    ):
        configuration_file_v2 = ConfigurationFileV2(
            project_root_path=protostar_toml_path,
            configuration_file_interpreter=ConfigurationTOMLInterpreter(
                file_content=protostar_toml_content
            ),
            filename=protostar_toml_path.name,
        )
        if configuration_file_v2.get_declared_protostar_version() is not None:
            return configuration_file_v2
        return None

    def _create_configuration_toml_v1(
        self,
        protostar_toml_path: Path,
        protostar_toml_content: str,
    ):
        configuration_file_v1 = ConfigurationFileV1(
            project_root_path=protostar_toml_path,
            configuration_file_interpreter=ConfigurationLegacyTOMLInterpreter(
                file_content=protostar_toml_content
            ),
            filename=protostar_toml_path.name,
        )
        if configuration_file_v1.get_declared_protostar_version() is not None:
            return configuration_file_v1
        return None

    def _search_upwards_protostar_toml_path(self) -> Optional[Path]:
        directory_path = self._cwd
        root_path = Path(directory_path.root)
        while directory_path != root_path:
            for file_path in directory_path.iterdir():
                if "protostar.toml" == file_path.name:
                    return directory_path / "protostar.toml"

            directory_path = directory_path.parent
        return None
