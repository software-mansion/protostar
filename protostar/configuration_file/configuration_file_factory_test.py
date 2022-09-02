from pathlib import Path

from .configuration_file_factory import ConfigurationFileFactory


def test_not_finding_protostar_toml(tmp_path: Path):
    path = ConfigurationFileFactory(tmp_path).search_upwards_protostar_toml_path()
    assert path is None


def test_searching_protostar_from_cwd(tmp_path: Path):
    protostar_toml_path = tmp_path / "protostar.toml"
    protostar_toml_path.touch()

    result = ConfigurationFileFactory(tmp_path).search_upwards_protostar_toml_path()

    assert result == protostar_toml_path


def test_searching_protostar_toml_when_cwd_below_project_root(tmp_path: Path):
    project_root_path = tmp_path
    src_path = project_root_path / "src"
    src_path.mkdir()
    protostar_toml_path = project_root_path / "protostar.toml"
    protostar_toml_path.touch()

    result = ConfigurationFileFactory(src_path).search_upwards_protostar_toml_path()

    assert result == protostar_toml_path
