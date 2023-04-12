import pytest
from pytest import CaptureFixture

from tests.data.contracts import EMPTY_TEST
from tests.integration.conftest import (
    CreateProtostarProjectFixture,
    ProtostarProjectFixture,
)


@pytest.fixture(autouse=True, name="protostar_project")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar_project:
        yield protostar_project


async def test_gas_estimation(
    protostar_project: ProtostarProjectFixture,
    capsys: CaptureFixture[str],
):
    await protostar_project.protostar.test(
        targets=["::test_increase_balance"], estimate_gas=True
    )

    assert "gas=4852" in capsys.readouterr().out


async def test_gas_estimation_for_empty_function(
    protostar_project: ProtostarProjectFixture,
    capsys: CaptureFixture[str],
):
    protostar_project.create_files({"tests/test_main.cairo": EMPTY_TEST})
    await protostar_project.protostar.test(
        targets=["::test_nothing"], estimate_gas=True
    )

    assert "gas=4556" in capsys.readouterr().out
