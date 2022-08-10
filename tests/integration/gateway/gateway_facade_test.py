from pathlib import Path

import pytest

from protostar.starknet_gateway.gateway_facade import GatewayFacade
from protostar.utils.log_color_provider import LogColorProvider


@pytest.fixture(autouse=True, scope="module")
# pylint: disable=unused-argument
def testing_environment(standard_project, compiled_project):
    pass


async def test_deploy(gateway_facade: GatewayFacade, compiled_contract_path: Path):
    response = await gateway_facade.deploy(compiled_contract_path)
    assert response is not None


async def test_declare(gateway_facade: GatewayFacade, compiled_contract_path: Path):
    response = await gateway_facade.declare(compiled_contract_path)
    assert response is not None


async def test_invoke(gateway_facade: GatewayFacade, compiled_contract_path: Path):
    deployed_contract = await gateway_facade.deploy(compiled_contract_path)

    response = await gateway_facade.invoke(
        deployed_contract.address,
        function_name="increase_balance",
        inputs={"amount": 42},
        wait_for_acceptance=True,
    )

    assert response is not None


async def test_call(gateway_facade: GatewayFacade, compiled_contract_path: Path):
    deployed_contract = await gateway_facade.deploy(compiled_contract_path)

    response = await gateway_facade.call(
        deployed_contract.address,
        function_name="get_balance",
        inputs={},
    )

    assert response is not None


@pytest.fixture(name="gateway_facade")
def gateway_facade_fixture(devnet_gateway_url: str):
    log_color_provider = LogColorProvider()
    log_color_provider.is_ci_mode = False
    gateway_facade_builder = GatewayFacade.Builder(project_root_path=Path())
    gateway_facade_builder.set_network(devnet_gateway_url)
    return gateway_facade_builder.build()


@pytest.fixture(name="compiled_contract_path")
def compiled_contract_path_fixture(project_compilation_output_path: Path) -> Path:
    return project_compilation_output_path / "main.json"
