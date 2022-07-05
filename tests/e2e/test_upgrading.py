import pytest

from tests.e2e.conftest import ProtostarFixture


@pytest.mark.parametrize("declared_protostar_version", ["0.0.0"])
@pytest.mark.usefixtures("init")
def test_upgrading(protostar: ProtostarFixture):
    result = protostar(["--version"])
    assert "0.0.0" in result

    protostar(["upgrade"])

    result = protostar(["--version"])
    assert "0.0.0" not in result
