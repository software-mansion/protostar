from os import listdir

import pytest

from tests.e2e.conftest import ProtostarFixture


@pytest.mark.usefixtures("init_cairo1")
def test_default_build(protostar: ProtostarFixture):
    protostar(["build-cairo1"])
    dirs = listdir()
    assert "build" in dirs
