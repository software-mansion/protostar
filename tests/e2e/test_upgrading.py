import pytest

from tests.e2e.conftest import ProtostarFixture


@pytest.mark.parametrize("protostar_version", ["0.0.0"])
@pytest.mark.usefixtures("init")
def test_upgrading(protostar: ProtostarFixture):
    assert "0.0.0" in protostar(["--version"])
    assert "ERROR" not in protostar(["upgrade"])
    assert "0.0.0" not in protostar(["--version"])


@pytest.mark.parametrize("protostar_version", ["0.0.0"])
@pytest.mark.usefixtures("init")
def test_upgrade_notification(protostar: ProtostarFixture):
    protostar(["build"])
    assert "new Protostar version" in protostar(["build"])
