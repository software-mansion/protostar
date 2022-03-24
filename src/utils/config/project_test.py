from pathlib import Path

import pytest

from src.utils.config.project import (
    Project,
    ProjectConfig,
    NoProtostarProjectFoundError,
)

current_directory = Path(__file__).parent


def make_mock_project(mocker, contracts, libs_path, pkg_root=None) -> Project:
    pkg = Project(pkg_root)
    mock_config = ProjectConfig(
        name="",
        description="",
        license="",
        version="",
        authors=[""],
        contracts=contracts,
        libs_path=libs_path,
    )
    mocker.patch.object(pkg, attribute="load_config").return_value = mock_config
    mocker.patch.object(pkg, attribute="_config", new=mock_config)
    return pkg


def test_parsing_project_info():
    proj = Project(project_root=Path(current_directory, "examples"))
    config = proj.load_config()
    assert config.name == "testproj"
    assert config.description == "descr"
    assert config.license == "MIT"
    assert config.version == "1.0"
    assert config.authors == [
        "tomekgsd@gmail.com",
    ]
    assert config.libs_path == "lib"


def test_no_project_found():
    proj = Project.get_current()
    with pytest.raises(NoProtostarProjectFoundError):
        proj.load_config()
