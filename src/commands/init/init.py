from collections import OrderedDict
from pathlib import Path
import shutil

import tomli_w
from colorama import Fore


def init(script_root: str):
    """
    Creates init protostar project
    """
    project_name = input(f"{Fore.CYAN}Project name: ")

    project_path = Path() / project_name
    copy_template(script_root, "default", project_path)

    package = PackageConfig(project_path=project_path)

    package.name = project_name

    project_description = input(f"{Fore.CYAN}Project description: ")
    package.description = project_description

    author = input(f"{Fore.CYAN}Author: ")
    package.authors = [author]

    version = input(f"{Fore.CYAN}Version: ")
    package.version = version

    project_license = input(f"{Fore.CYAN}License: ")
    package.license = project_license

    package.write()


def copy_template(script_root: str, template_name: str, project_path: Path):
    template_path = f"{script_root}/templates/{template_name}"
    shutil.copytree(template_path, project_path)


class PackageConfig:
    # pylint: disable=too-many-instance-attributes
    general_props = ["name", "description", "license", "version", "authors"]

    def __init__(self, project_path=None):
        self._project_path = project_path
        self.name = "package_name"
        self.description = ""
        self.license = ""
        self.version = "0.1.0"
        self.authors = []
        self.contracts = []

    @property
    def project_path(self) -> Path:
        return self._project_path if self._project_path else Path()

    @property
    def config_path(self) -> Path:
        return self.project_path / "package.toml"

    @property
    def config_dict(self):
        obj_dict = self.__dict__
        result = OrderedDict()
        result["protostar.general"] = {key: obj_dict[key] for key in self.general_props}
        result["protostar.contracts"] = {"main": ["src/main.cairo"]}
        return result

    def write(self):
        with open(self.config_path, "wb") as file:
            tomli_w.dump(self.config_dict, file)
