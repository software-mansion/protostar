from pathlib import Path
from typing import Optional

from protostar.configuration_file.configuration_file_v1 import ConfigurationFileV1
from protostar.configuration_file.configuration_toml_reader import (
    ConfigurationTOMLReader,
)

from .configuration_file import ConfigurationFile


class ConfigurationFileFactory:
    def create_configuration_file(self, cwd: Path) -> Optional[ConfigurationFile]:
        configuration_file_path = self._find_configuration_file_path(cwd)
        if configuration_file_path is None:
            return None
        configuration_toml_reader = ConfigurationTOMLReader(
            path=configuration_file_path
        )
        return ConfigurationFileV1(
            configuration_toml_reader=configuration_toml_reader,
            project_root_path=self.get_project_root(configuration_file_path),
        )

    def get_project_root(self, configuration_file_path: Path) -> Path:
        return configuration_file_path.parent

    def _find_configuration_file_path(self, cwd: Path) -> Optional[Path]:
        start_path = cwd
        root_path = Path(start_path.root)
        while start_path != root_path:
            for file_path in start_path.iterdir():
                if "protostar.toml" == file_path.name:
                    return start_path / "protostar.toml"
            start_path = start_path.parent
        return None
