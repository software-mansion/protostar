from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional

import tomli
import tomli_w


class NoProtostarProjectFoundError(Exception):
    pass


@dataclass
class ProjectConfig:
    name: str = field(default="project_name")
    description: str = field(default="")
    license: str = field(default="")
    version: str = field(default="0.1.0")
    authors: List[str] = field(default_factory=list)
    contracts: Dict[str, List[str]] = field(
        default_factory=lambda: {"main": ["src/main.cairo"]}
    )
    libs_path: str = field(default="lib")


class Project:
    @classmethod
    def get_current(cls):
        return cls()

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path()
        self.config = None

    @property
    def config_path(self) -> Path:
        assert self.project_root, "No project_path provided!"
        return self.project_root / "protostar.toml"

    @property
    def ordered_dict(self):
        general = OrderedDict(**self.config.__dict__)
        general.pop("contracts")

        result = OrderedDict()
        result["protostar.general"] = general
        assert self.config, "No package configuration loaded!"
        result["protostar.contracts"] = self.config.contracts
        return result

    def write_config(self, config: ProjectConfig):
        self.config = config
        with open(self.config_path, "wb") as file:
            tomli_w.dump(self.ordered_dict, file)

    def load_config(self) -> "ProjectConfig":
        if not self.config_path.is_file():
            raise NoProtostarProjectFoundError(
                "No protostar.toml found in the working directory"
            )

        with open(self.config_path, "rb") as config_file:
            parsed_config = tomli.load(config_file)

            flat_config = {
                **parsed_config["protostar.general"],
                "contracts": parsed_config["protostar.contracts"],
            }
            self.config = ProjectConfig(**flat_config)
            return self.config
