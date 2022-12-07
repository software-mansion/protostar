import pytest
from pytest import CaptureFixture

from tests.data.contracts import EMPTY_TEST
from tests.integration.conftest import CreateProtostarProjectFixture, ProtostarFixture


@pytest.fixture(autouse=True, name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        yield protostar


async def test_gas_estimation(
    protostar: ProtostarFixture,
    capsys: CaptureFixture[str],
):
    await protostar.test(targets=["::test_increase_balance"], estimate_gas=True)

    assert "gas=4356" in capsys.readouterr().out


async def test_gas_estimation_for_identity_function(
    protostar: ProtostarFixture,
    capsys: CaptureFixture[str],
):
    protostar.create_files({"tests/test_main.cairo": EMPTY_TEST})
    await protostar.test(targets=["::test_nothing"], estimate_gas=True)

    assert "gas=4068" in capsys.readouterr().out
