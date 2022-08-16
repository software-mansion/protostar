from pathlib import Path

import pytest

from protostar.starknet_gateway.gateway_facade import (
    ContractNotFoundException,
    GatewayFacade,
    UnknownFunctionException,
)
from protostar.utils.log_color_provider import LogColorProvider
from tests.integration.protostar_fixture import ProtostarFixture


@pytest.fixture(autouse=True, scope="module")
def setup(protostar: ProtostarFixture):
    protostar.init_sync()
    protostar.build_sync()


@pytest.fixture(name="compiled_contract_path")
def compiled_contract_path_fixture(protostar: ProtostarFixture) -> Path:
    return protostar.project_root_path / "build" / "main.json"


@pytest.fixture(name="gateway_facade")
def gateway_facade_fixture(devnet_gateway_url: str):
    log_color_provider = LogColorProvider()
    log_color_provider.is_ci_mode = False
    gateway_facade_builder = GatewayFacade.Builder(project_root_path=Path())
    gateway_facade_builder.set_network(devnet_gateway_url)
    return gateway_facade_builder.build()


async def test_deploy(gateway_facade: GatewayFacade, compiled_contract_path: Path):
    response = await gateway_facade.deploy(compiled_contract_path)
    assert response is not None


async def test_declare(gateway_facade: GatewayFacade, compiled_contract_path: Path):
    response = await gateway_facade.declare(compiled_contract_path)
    assert response is not None


async def test_call(gateway_facade: GatewayFacade, compiled_contract_path: Path):
    deployed_contract = await gateway_facade.deploy(compiled_contract_path)

    response = await gateway_facade.call(
        deployed_contract.address,
        function_name="get_balance",
        inputs={},
    )

    initial_balance = 0
    assert response[0] == initial_balance


async def test_call_to_unknown_function(
    gateway_facade: GatewayFacade, compiled_contract_path: Path
):
    deployed_contract = await gateway_facade.deploy(compiled_contract_path)

    with pytest.raises(UnknownFunctionException):
        await gateway_facade.call(
            deployed_contract.address,
            function_name="UNKNOWN_FUNCTION",
            inputs={},
        )


async def test_call_to_unknown_contract(gateway_facade: GatewayFacade):
    with pytest.raises(ContractNotFoundException):
        await gateway_facade.call(
            123,
            function_name="UNKNOWN_FUNCTION",
        )


@pytest.mark.skip("https://github.com/software-mansion/starknet.py/issues/302")
async def test_call_to_with_incorrect_args(
    gateway_facade: GatewayFacade, compiled_contract_path: Path
):
    deployed_contract = await gateway_facade.deploy(compiled_contract_path)

    with pytest.raises(Exception):
        await gateway_facade.call(
            deployed_contract.address,
            function_name="get_balance",
            inputs={"UNKNOWN_ARG": 42},
        )


async def test_call_to_with_positional_incorrect_args(
    gateway_facade: GatewayFacade, compiled_contract_path: Path
):
    deployed_contract = await gateway_facade.deploy(compiled_contract_path)

    with pytest.raises(Exception):
        await gateway_facade.call(
            deployed_contract.address,
            function_name="get_balance",
            inputs=[42],
        )
