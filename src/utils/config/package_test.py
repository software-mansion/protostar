from pathlib import Path

import pytest

from src.utils.config.package import Package, PackageConfig, NoProtostarPackageFoundError

current_directory = Path(__file__).parent


def mock_package(mocker, contracts, libs_path, pkg_root=None) -> Package:
    pkg = Package(pkg_root)
    mock_config = PackageConfig(
        name="",
        description="",
        license="",
        version="",
        authors=[""],
        contracts=contracts,
        libs_path=libs_path,
    )
    mocker.patch.object(pkg, attribute="load_config").return_value = mock_config
    return pkg


def test_parsing_pkg_info():
    pkg = Package(project_root=Path(current_directory, "examples"))
    config = pkg.load_config()
    assert config.name == "testproj"
    assert config.description == "descr"
    assert config.license == "MIT"
    assert config.version == "1.0"
    assert config.authors == [
        "tomekgsd@gmail.com",
    ]
    assert config.libs_path == "lib"


def test_no_pkg_found():
    pkg = Package.current()
    with pytest.raises(NoProtostarPackageFoundError):
        pkg.load_config()
