from pathlib import Path

import pytest

from protostar.starknet_gateway.gateway_facade import GatewayFacade
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
