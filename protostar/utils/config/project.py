from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

import flatdict
import tomli
import tomli_w

from protostar.commands.test.expected_event import collect_immediate_subdirectories
from protostar.protostar_exception import ProtostarException
from protostar.utils.protostar_directory import VersionManager


class NoProtostarProjectFoundException(ProtostarException):
    pass


class VersionNotSupportedException(ProtostarException):
    pass


@dataclass
class ProtostarConfig:
    protostar_version: str = field(default="0.1.0")


@dataclass
class ProjectConfig:
    libs_path: str = field(default="./lib")
    contracts: Dict[str, List[str]] = field(
        default_factory=lambda: {"main": ["./src/main.cairo"]}
    )


class Project:
    def __init__(
        self, version_manager: VersionManager, project_root: Optional[Path] = None
    ):
        self.project_root = project_root or Path()
        self.shared_command_configs_section_name = "shared_command_configs"
        self._project_config = None
        self._protostar_config = None
        self._version_manager = version_manager
        self._config_dict: Optional[Dict[str, Any]] = None

    @property
    def libs_path(self) -> Path:
        return self.project_root.resolve() / self.config.libs_path

    @property
    def config(self) -> ProjectConfig:
        if not self._project_config:
            self.load_config()
        return cast(ProjectConfig, self._project_config)

    @property
    def config_path(self) -> Path:
        return self.project_root / "protostar.toml"

    @property
    def ordered_dict(self):
        general = OrderedDict(**self.config.__dict__)
        general.pop("contracts")

        protostar_config = ProtostarConfig()

        result = OrderedDict()
        result["protostar.config"] = OrderedDict(protostar_config.__dict__)
        result["protostar.project"] = general
        result["protostar.contracts"] = self.config.contracts
        return result

    def get_include_paths(self) -> List[str]:
        libs_path = Path(self.project_root, self.config.libs_path)
        return [
            str(self.project_root),
            str(libs_path),
            *collect_immediate_subdirectories(libs_path),
        ]

    def write_config(self, config: ProjectConfig):
        self._project_config = config
        with open(self.config_path, "wb") as file:
            tomli_w.dump(self.ordered_dict, file)

    def load_argument(self, section_name: str, attribute_name: str) -> Optional[Any]:
        assert not section_name.startswith("protostar.")

        if not self._config_dict:
            try:
                with open(self.config_path, "rb") as config_file:
                    self._config_dict = tomli.load(config_file)
            except FileNotFoundError:
                return None

        flat_config = flatdict.FlatDict(self._config_dict, delimiter=".")

        section_name = f"protostar.{section_name}"
        if section_name not in flat_config:
            return None
        section_config = flat_config[section_name]
        attribute_name = attribute_name.replace("-", "_")
        if attribute_name not in section_config:
            return None
        return section_config[attribute_name]

    def load_config(self) -> "ProjectConfig":
        if not self.config_path.is_file():
            raise NoProtostarProjectFoundException(
                "No protostar.toml found in the working directory"
            )

        with open(self.config_path, "rb") as config_file:
            parsed_config = tomli.load(config_file)

            flat_config = {
                **parsed_config["protostar.project"],
                "contracts": parsed_config["protostar.contracts"],
            }
            self._project_config = ProjectConfig(**flat_config)

            self._protostar_config = ProtostarConfig(
                **parsed_config["protostar.config"],
            )

            config_protostar_version = self._version_manager.parse(
                self._protostar_config.protostar_version
            )

            if (
                self._version_manager.protostar_version
                or VersionManager.parse("99.99.99")
            ) < config_protostar_version:
                raise VersionNotSupportedException(
                    (
                        # pylint: disable=line-too-long
                        f"Current Protostar build ({self._version_manager.protostar_version}) doesn't support protostar_version {config_protostar_version}\n"
                        "Try upgrading protostar by running: protostar upgrade"
                    )
                )

            return self._project_config

    def load_protostar_config(self) -> ProtostarConfig:
        if not self.config_path.is_file():
            raise NoProtostarProjectFoundException(
                "No protostar.toml found in the working directory"
            )

        with open(self.config_path, "rb") as config_file:
            parsed_config = tomli.load(config_file)

            self._protostar_config = ProtostarConfig(
                **parsed_config["protostar.config"]
            )
            return self._protostar_config
