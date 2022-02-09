from collections import OrderedDict
from pathlib import Path
import tomli_w


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
        self.dependencies = []
        self.dev_dependencies = []

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
        result["protostar.dependencies"] = {}
        result["protostar.dev-dependencies"] = {}
        return result

    def write(self):
        with open(self.config_path, "wb") as file:
            tomli_w.dump(self.config_dict, file)
