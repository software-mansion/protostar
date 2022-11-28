import pytest
from pytest import CaptureFixture

from tests.integration.conftest import CreateProtostarProjectFixture, ProtostarFixture
from tests.conftest import DevnetFixture


@pytest.fixture(autouse=True, name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        protostar.build_sync()
        yield protostar


async def test_gas_estimation(
    protostar: ProtostarFixture,
    capsys: CaptureFixture[str],
):
    await protostar.test(targets=["::test_increase_balance"], estimate_gas=True)

    assert "gas=4059" in capsys.readouterr().out
