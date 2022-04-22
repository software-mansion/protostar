from pathlib import Path

from src.core.application import Application
from src.core.command import Command
from src.utils.config.project import Project
from src.utils.protostar_directory import ProtostarDirectory, VersionManager

protostar_directory = ProtostarDirectory(Path(__file__).parent / "..")
version_manager = VersionManager(protostar_directory)
current_project = Project(version_manager)

protostar_app = Application(
    root_args=[
        Command.Argument(
            name="version",
            short_name="v",
            input_type="bool",
            description="Show Protostar and Cairo-lang version.",
        )
    ]
)
