import pytest

from tests.e2e.conftest import ProtostarFixture


@pytest.mark.parametrize("declared_protostar_version", ["0.0.0"])
@pytest.mark.usefixtures("init")
def test_upgrading(protostar: ProtostarFixture):
    assert "0.0.0" in protostar(["--version"])
    assert "ERROR" not in protostar(["upgrade"])
    assert "0.0.0" not in protostar(["--version"])


@pytest.mark.parametrize("declared_protostar_version", ["0.2.0"])
@pytest.mark.usefixtures("init")
def test_upgrade_notification(protostar: ProtostarFixture):
    assert "new Protostar version" not in protostar(["test"])
    assert "new Protostar version" in protostar(["test"])
