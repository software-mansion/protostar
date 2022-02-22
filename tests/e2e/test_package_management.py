from os import listdir

import pytest


@pytest.mark.usefixtures("init")
def test_package_installation(protostar):
    with pytest.raises(FileNotFoundError):
        assert "starknet_py" not in listdir("lib")

    result = protostar(["install", "https://github.com/software-mansion/starknet.py"])

    print("result", result)
    assert "Installing starknet_py" in result
    assert "starknet_py" in listdir("lib")
