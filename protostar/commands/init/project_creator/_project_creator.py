import shutil
from abc import ABC, abstractmethod
from pathlib import Path

from typing_extensions import Literal


class ProjectCreator(ABC):
    def __init__(self, script_root: Path):
        self.script_root = script_root

    def copy_template(self, template_name: Literal["default"], project_root_path: Path):
        template_path = self.script_root / "templates" / template_name
        shutil.copytree(template_path, project_root_path)

    @abstractmethod
    def run(self) -> None:
        ...
