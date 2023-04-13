import os
from pathlib import Path
from typing import Dict, Union, Generator, Any
from contextlib import contextmanager
import shutil

from pytest_mock import MockerFixture

from tests.conftest import ProtostarTmpPathFactory

from protostar.configuration_file import (
    ConfigurationFileV2Model,
    ConfigurationFileV2,
)
from protostar.configuration_file.configuration_toml_interpreter import (
    ConfigurationTOMLInterpreter,
)
from protostar.cairo import CairoVersion
from protostar.configuration_file import (
    ConfigurationFileV2ContentFactory,
    ConfigurationTOMLContentBuilder,
)
from .protostar_fixture_factory import create_protostar_fixture


@contextmanager
# pylint: disable=unused-argument
def fake_activity_indicator(message: str) -> Generator[None, None, None]:
    yield


class ProtostarProjectFixture:
    def __init__(
        self,
        mocker: MockerFixture,
        tmp_path_factory: ProtostarTmpPathFactory,
        cairo_version: CairoVersion = CairoVersion.cairo0,
    ) -> None:
        self._mocker = mocker
        self._tmp_path_factory = tmp_path_factory

        tmp_path = self._tmp_path_factory()
        self._project_root_path = tmp_path

        self.cwd = None
        self.protostar = self.create_protostar_fixture(
            self._mocker, self._project_root_path
        )
        self._create_protostar_project(cairo_version)

    def _create_protostar_project(self, cairo_version: CairoVersion):
        self.cwd = Path().resolve()

        project_name = "project_name"
        if cairo_version == CairoVersion.cairo0:
            self.protostar.init_sync(project_name)
        else:
            self.protostar.init_cairo1_sync(project_name)

        self._project_root_path = self._project_root_path / project_name
        os.chdir(self._project_root_path)
        # rebuilding protostar fixture to reload configuration file
        self.protostar = self.create_protostar_fixture(
            self._mocker, self._project_root_path
        )

    def __enter__(self):
        return self

    def __exit__(self, *args: Any, **kwargs: Any):
        assert self.cwd
        os.chdir(self.cwd)

    def create_protostar_fixture(self, mocker: MockerFixture, project_root_path: Path):
        return create_protostar_fixture(mocker, project_root_path)

    @property
    def project_root_path(self) -> Path:
        return self._project_root_path

    def create_files(
        self, relative_path_str_to_file: Dict[str, Union[str, Path]]
    ) -> None:
        for relative_path_str, file in relative_path_str_to_file.items():
            if isinstance(file, Path):
                content = file.read_text("utf-8")
            else:
                content = file
            self._save_file(self._project_root_path / relative_path_str, content)

    def create_contracts(self, contract_name_to_file: Dict[str, Union[str, Path]]):
        relative_path_str_to_file = {
            f"src/{contract_name}.cairo": file
            for contract_name, file in contract_name_to_file.items()
        }
        self.create_files(relative_path_str_to_file)
        self.add_contracts_to_protostar_toml(contract_name_to_file)
        self.protostar = self.create_protostar_fixture(
            self._mocker, self._project_root_path
        )

    def create_contracts_cairo1(
        self, contract_name_to_contract_dir: Dict[str, Union[str, Path]]
    ):
        for contract_name, contract_dir in contract_name_to_contract_dir.items():
            assert Path(
                contract_dir
            ).is_dir(), "contracts in cairo1 should be represented as directories"
            relative_path = f"src/{contract_name}"
            shutil.copytree(contract_dir, self._project_root_path / relative_path)
        self.add_contracts_to_protostar_toml(contract_name_to_contract_dir)
        self.protostar = self.create_protostar_fixture(
            self._mocker, self._project_root_path
        )

    def add_contracts_to_protostar_toml(
        self, contract_name_to_file: Dict[str, Union[str, Path]]
    ):
        protostar_toml_path = self.project_root_path / "protostar.toml"
        assert (
            protostar_toml_path.is_file()
        ), "No protostar.toml found, cannot change contents."

        interpreter = ConfigurationTOMLInterpreter(
            protostar_toml_path.read_text("utf-8")
        )
        config_file_v2 = ConfigurationFileV2(
            project_root_path=self.project_root_path,
            configuration_file_interpreter=interpreter,
            file_path=protostar_toml_path,
            active_profile_name=None,
        )

        previous_contract_map = {
            contract_name: [
                str(src_path)
                for src_path in config_file_v2.get_contract_source_paths(contract_name)
            ]
            for contract_name in config_file_v2.get_contract_names()
        }

        new_contract_map = {
            contract_name: [str(file_path.resolve())]
            if isinstance(file_path, Path)
            else [file_path]
            for contract_name, file_path in contract_name_to_file.items()
        }

        declared_protostar_v = config_file_v2.get_declared_protostar_version()
        declared_protostar_v_str = (
            str(declared_protostar_v) if declared_protostar_v else None
        )
        overriden_config_file_model_v2 = ConfigurationFileV2Model(
            protostar_version=declared_protostar_v_str,
            contract_name_to_path_strs={
                **previous_contract_map,
                **new_contract_map,
            },
            project_config={},
            command_name_to_config={},
            profile_name_to_project_config={},
            profile_name_to_commands_config={},
        )
        content_factory = ConfigurationFileV2ContentFactory(
            content_builder=ConfigurationTOMLContentBuilder()
        )
        file_content = content_factory.create_file_content(
            overriden_config_file_model_v2
        )
        protostar_toml_path.write_text(file_content)

    @staticmethod
    def _save_file(path: Path, content: str) -> None:
        path.parent.mkdir(exist_ok=True, parents=True)
        with open(
            path,
            mode="w",
            encoding="utf-8",
        ) as output_file:
            output_file.write(content)
