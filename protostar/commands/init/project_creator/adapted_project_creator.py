from pathlib import Path

from protostar.commands.init.project_creator._project_creator import ProjectCreator
from protostar.protostar_toml.io.protostar_toml_writer import ProtostarTOMLWriter
from protostar.self.protostar_directory import VersionManager
from protostar.io.input_requester import InputRequester
from protostar.git import Git


class AdaptedProjectCreator(ProjectCreator):
    def __init__(
        self,
        script_root: Path,
        requester: InputRequester,
        protostar_toml_writer: ProtostarTOMLWriter,
        version_manager: VersionManager,
    ):
        super().__init__(script_root, protostar_toml_writer, version_manager)
        self._protostar_toml_writer = protostar_toml_writer
        self._version_manager = version_manager
        self._requester = requester

    def run(self):
        project_root_path = Path()
        libs_path = project_root_path / self.default_lib_dirname

        if not libs_path.is_dir():
            libs_path.mkdir(parents=True)

        self.save_protostar_toml(project_root=project_root_path)

        Git.init(project_root_path)
