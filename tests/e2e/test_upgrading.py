import pytest

from tests.e2e.conftest import ProtostarFixture


@pytest.mark.parametrize("protostar_version", ["0.0.0"])
@pytest.mark.usefixtures("init")
@pytest.mark.skip(
    "Protostar 0.9.1 installation fails on Ubuntu 20.04. Remove the skip, after a new release build on Ubuntu 20.04."
)
def test_upgrading(protostar: ProtostarFixture):
    assert "0.0.0" in protostar(["--version"])
    assert "ERROR" not in protostar(["upgrade"])
    assert "0.0.0" not in protostar(["--version"])


@pytest.mark.parametrize("protostar_version", ["0.0.0"])
@pytest.mark.usefixtures("init")
def test_upgrade_notification(protostar: ProtostarFixture):
    protostar(["build"])
    assert "new Protostar version" in protostar(["build"])


@pytest.mark.parametrize("protostar_version", ["0.0.0"])
def test_upgrade_notification_not_on_upgrade(protostar: ProtostarFixture):
    assert "new Protostar version" not in protostar(["upgrade"])
