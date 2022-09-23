# pylint: disable=unused-argument
from os import chdir, listdir, getcwd
from os import replace as move
from pathlib import Path
from typing import Optional

import pytest


@pytest.fixture(name="project_new_location")
def project_new_location_fixture() -> Optional[Path]:
    return None


@pytest.fixture(name="project_relocator")
def project_relocator_fixture(init, project_new_location: Optional[Path]):
    print("TEST")
    if not project_new_location:
        return

    print("TEST2")

    project_content = listdir()
    project_new_location.mkdir(parents=True)
    for file_or_dir in project_content:
        if file_or_dir != ".git":
            move(file_or_dir, project_new_location / file_or_dir)

    import glob

    print("PRE", getcwd())
    print(*listdir(), sep="\n")
    print(*list(glob.iglob(r"**/**", recursive=True)), sep="\n")
    chdir(project_new_location)
    print("POST", getcwd())


@pytest.fixture(name="install_package")
def fixture_install_package(init, protostar):
    def install_package():
        result = protostar(
            ["--no-color", "install", "https://github.com/software-mansion/starknet.py"]
        )
        normalized_package_name = "starknet_py"
        return (result, normalized_package_name)

    return install_package


@pytest.mark.parametrize("libs_path", ["lib", "deps"])
@pytest.mark.parametrize("project_new_location", [None, Path("./subproject")])
@pytest.mark.usefixtures("project_relocator")
def test_adding_package(install_package, libs_path: str):
    with pytest.raises(FileNotFoundError):
        listdir(f"{libs_path}/starknet_py")

    (result, normalized_package_name) = install_package()

    assert f"Installing {normalized_package_name}" in result
    assert normalized_package_name in listdir(libs_path)


@pytest.mark.parametrize("libs_path", ["lib", "deps"])
@pytest.mark.parametrize("project_new_location", [None, Path("./subproject")])
@pytest.mark.usefixtures("project_relocator")
def test_updating_package(install_package, protostar, libs_path):
    install_package()

    result = protostar(["--no-color", "update", "starknet_py"])

    assert "Updating starknet_py" in result
    assert "starknet_py" in listdir(libs_path)


@pytest.mark.parametrize("libs_path", ["lib", "deps"])
@pytest.mark.parametrize("project_new_location", [None, Path("./subproject")])
@pytest.mark.usefixtures("project_relocator")
def test_removing_package(install_package, protostar, libs_path):
    install_package()

    print(f"DIR({getcwd()}): {listdir()}")

    result = protostar(["--no-color", "remove", "starknet_py"])

    assert "Removing starknet_py" in result
    assert "starknet_py" not in listdir(libs_path)
