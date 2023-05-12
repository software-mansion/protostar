from pathlib import Path

from protostar.commands.legacy_commands.init_cairo0.project_creator import (
    ProjectCreator,
)
from protostar.configuration_file import ConfigurationFileV2Model


class AdaptedProjectCreator(ProjectCreator):
    def run(self):
        project_root_path = Path()
        config = ConfigurationFileV2Model(
            protostar_version=str(self._protostar_version),
            contract_name_to_path_strs={"main": ["src/main.cairo"]},
            project_config={
                "lib-path": "lib",
            },
        )

        self._write_protostar_toml_from_config(
            project_root_path=project_root_path, configuration_model=config
        )
