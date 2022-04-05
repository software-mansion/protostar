from pathlib import Path

import pytest

from src.utils.config.project import (
    NoProtostarProjectFoundError,
    Project,
    ProjectConfig,
    VersionNotSupportedException,
)

current_directory = Path(__file__).parent


def make_mock_project(mocker, contracts, libs_path, pkg_root=None) -> Project:
    pkg = Project(pkg_root)
    mock_config = ProjectConfig(
        contracts=contracts,
        libs_path=libs_path,
    )
    mocker.patch.object(pkg, attribute="load_config").return_value = mock_config
    mocker.patch.object(pkg, attribute="_config", new=mock_config)
    return pkg


def test_parsing_project_info():
    proj = Project(project_root=Path(current_directory, "examples", "standard"))
    config = proj.load_config()
    assert config.libs_path == "./lib"


def test_config_file_is_versioned():
    proj = Project(project_root=Path(current_directory, "examples", "standard"))
    protostar_config = proj.load_protostar_config()
    assert protostar_config.config_version == "0.1.0"


def test_handling_not_supported_version():
    proj = Project(
        project_root=Path(current_directory, "examples", "unsupported_config")
    )
    with pytest.raises(VersionNotSupportedException):
        proj.load_config()


def test_no_project_found():
    proj = Project.get_current()
    with pytest.raises(NoProtostarProjectFoundError):
        proj.load_config()
