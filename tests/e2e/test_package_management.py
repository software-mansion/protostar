from os import listdir

import pytest


@pytest.fixture(name="install_package")
# pylint: disable=unused-argument
def fixture_install_package(init, protostar):
    def install_package():
        result = protostar(
            ["install", "https://github.com/software-mansion/starknet.py"]
        )
        normalized_package_name = "starknet_py"
        return (result, normalized_package_name)

    return install_package


@pytest.mark.parametrize("libs_path", ["lib", "deps"])
def test_adding_package(install_package, libs_path: str):
    with pytest.raises(FileNotFoundError):
        listdir("lib/starknet_py")

    (result, normalized_package_name) = install_package()

    assert f"Installing {normalized_package_name}" in result
    assert normalized_package_name in listdir(libs_path)


@pytest.mark.parametrize("libs_path", ["lib", "deps"])
def test_updating_package(install_package, protostar, libs_path):
    install_package()

    result = protostar(["update", "starknet_py"])

    assert "Updating starknet_py" in result
    assert "starknet_py" in listdir(libs_path)


@pytest.mark.parametrize("libs_path", ["lib", "deps"])
def test_removing_package(install_package, protostar, libs_path):
    install_package()

    result = protostar(["remove", "starknet_py"])

    assert "Removing starknet_py" in result
    assert "starknet_py" not in listdir(libs_path)
