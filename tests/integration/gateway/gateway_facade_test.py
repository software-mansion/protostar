from pathlib import Path

import pytest

from protostar.starknet_gateway.gateway_facade import GatewayFacade
from protostar.utils.log_color_provider import LogColorProvider


async def test_deploy(gateway_facade: GatewayFacade, compiled_contract_path: Path):
    response = await gateway_facade.deploy(compiled_contract_path)

    assert response is not None


@pytest.fixture(name="gateway_facade")
def gateway_facade_fixture(devnet_gateway_url: str):
    log_color_provider = LogColorProvider()
    log_color_provider.is_ci_mode = False
    gateway_facade_builder = GatewayFacade.Builder(project_root_path=Path())
    gateway_facade_builder.set_network(devnet_gateway_url)
    return gateway_facade_builder.build()
