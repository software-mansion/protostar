from os import listdir
import pytest


@pytest.mark.usefixtures("init")
def test_default_build(protostar):
    protostar(["build"])
    dirs = listdir()
    assert "build" in dirs
