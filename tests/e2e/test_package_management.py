# pylint: disable=unused-argument
from os import chdir, listdir
from os import replace as move
from pathlib import Path
from typing import Callable, Optional

import pytest

from protostar.git import Git
from tests.e2e.conftest import InitFixture, ProtostarFixture


@pytest.fixture(name="project_new_location")
def project_new_location_fixture() -> Optional[Path]:
    return None


@pytest.fixture(name="project_relocator")
def project_relocator_fixture(init: InitFixture, project_new_location: Optional[Path]):
    if not project_new_location:
        return

    project_content = listdir()
    project_new_location.mkdir(parents=True)
    for file_or_dir in project_content:
        if file_or_dir != ".git":
            move(file_or_dir, project_new_location / file_or_dir)

    chdir(project_new_location)


InstallPackageFixture = Callable


@pytest.fixture(name="install_package")
def install_package_fixture(
    init: InitFixture, protostar: ProtostarFixture
) -> InstallPackageFixture:
    def install_package():
        result = protostar(
            [
                "--no-color",
                "install",
                "https://github.com/software-mansion/starknet.py",
            ]
        )
        normalized_package_name = "starknet_py"
        return (result, normalized_package_name)

    return install_package


@pytest.mark.parametrize("libs_path", ["lib", "deps"])
@pytest.mark.parametrize("project_new_location", [None, Path("./subproject")])
@pytest.mark.usefixtures("project_relocator")
def test_adding_package(install_package: InstallPackageFixture, libs_path: str):
    with pytest.raises(FileNotFoundError):
        listdir(f"{libs_path}/starknet_py")

    (result, normalized_package_name) = install_package()

    assert f"Installing {normalized_package_name}" in result
    assert "Fetching from the mainline" in result
    assert normalized_package_name in listdir(libs_path)


@pytest.mark.parametrize("libs_path", ["lib", "deps"])
@pytest.mark.parametrize("project_new_location", [None, Path("./subproject")])
@pytest.mark.usefixtures("project_relocator")
def test_updating_package(
    install_package: InstallPackageFixture, protostar: ProtostarFixture, libs_path: str
):
    install_package()

    result = protostar(["--no-color", "update", "starknet_py"])

    assert "Updating starknet_py" in result
    assert "starknet_py" in listdir(libs_path)


@pytest.mark.parametrize("libs_path", ["lib", "deps"])
@pytest.mark.parametrize("project_new_location", [None, Path("./subproject")])
@pytest.mark.usefixtures("project_relocator")
def test_removing_package(
    install_package: InstallPackageFixture, protostar: ProtostarFixture, libs_path: str
):
    install_package()

    result = protostar(["--no-color", "remove", "starknet_py"])

    assert "Removing starknet_py" in result
    assert "starknet_py" not in listdir(libs_path)


@pytest.mark.parametrize("libs_path", ["lib", "deps"])
@pytest.mark.parametrize("project_new_location", [None, Path("./subproject")])
@pytest.mark.usefixtures("project_relocator")
def test_install_remove_install(
    install_package: InstallPackageFixture, protostar: ProtostarFixture, libs_path: str
):
    install_package()
    assert "starknet_py" in listdir(libs_path)

    protostar(["--no-color", "remove", "starknet_py"])
    assert "starknet_py" not in listdir(libs_path)

    install_package()
    assert "starknet_py" in listdir(libs_path)


@pytest.mark.parametrize("libs_path", ["lib", "deps"])
@pytest.mark.parametrize("project_new_location", [None, Path("./subproject")])
@pytest.mark.usefixtures("project_relocator")
def test_install_specified_tag(protostar: ProtostarFixture, libs_path: str):
    protostar(["--no-color", "install", "software-mansion/starknet.py@0.6.2-alpha"])
    assert "starknet_py" in listdir(libs_path)

    repo = Git.load_existing_repo(Path(libs_path) / "starknet_py")
    assert repo.get_tag() == "0.6.2-alpha"
