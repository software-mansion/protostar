from pathlib import Path

import pytest

from protostar.protostar_exception import ProtostarException
from tests.integration.conftest import CreateProtostarProjectFixture
from tests.integration.protostar_fixture import ProtostarFixture


@pytest.fixture(name="protostar")
def protostar_fixture(create_protostar_project: CreateProtostarProjectFixture):
    with create_protostar_project() as protostar:
        protostar.create_files(
            {"src/main.cairo": Path(__file__).parent / "getter_contract.cairo"}
        )
        protostar.build_sync()
        yield protostar


async def test_call(
    protostar: ProtostarFixture,
    devnet_gateway_url: str,
):
    deploy_response = await protostar.deploy(
        contract=protostar.project_root_path / "build" / "main.json",
        gateway_url=devnet_gateway_url,
    )

    response = await protostar.call(
        contract_address=deploy_response.address,
        function_name="add_3",
        inputs=[3],
        gateway_url=devnet_gateway_url,
    )

    assert response.res == 6 # type: ignore


async def test_call_failure(
    protostar: ProtostarFixture,
    devnet_gateway_url: str,
):
    await protostar.build()
    deploy_response = await protostar.deploy(
        contract=protostar.project_root_path / "build" / "main.json",
        gateway_url=devnet_gateway_url,
    )

    with pytest.raises(ProtostarException, match="0 != 1"):
        await protostar.call(
            contract_address=deploy_response.address,
            function_name="error_call",
            inputs=[],
            gateway_url=devnet_gateway_url,
        )
