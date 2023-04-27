from argparse import Namespace
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest
from starknet_py.net.models import StarknetChainId

from protostar.cairo import cairo_bindings
from protostar.cli import MessengerFactory
from protostar.commands import DeclareCairo1Command
from protostar.compiler import ProjectCompiler
from protostar.io import log_color_provider
from protostar.starknet_gateway import GatewayFacadeFactory
from tests.conftest import DevnetAccount, SetPrivateKeyEnvVarFixture


@pytest.fixture(name="compiled_contract_path")
def compiled_contract_path_fixture() -> Path:
    return Path("./build/main.json")


@pytest.fixture(name="mocked_project_compiler")
def mocked_project_compiler_fixture(datadir: Path) -> ProjectCompiler:
    class MockedProjectCompiler(ProjectCompiler):
        def __init__(self):
            super().__init__(MagicMock(), MagicMock())

        def compile_contract_to_sierra_from_contract_name(
            self, *args: Any, **kwargs: Any
        ):
            # pylint: disable=unused-argument
            compiled = cairo_bindings.compile_starknet_contract_to_sierra_from_path(
                input_path=datadir,
            )
            assert compiled is not None
            return compiled

        def compile_contract_to_casm_from_contract_name(
            self, *args: Any, **kwargs: Any
        ):
            # pylint: disable=unused-argument
            compiled = cairo_bindings.compile_starknet_contract_to_casm_from_path(
                input_path=datadir,
            )
            assert compiled is not None
            return compiled

        def compile_contract(self, *args: Any, **kwargs: Any):
            sierra_compiled = self.compile_contract_to_sierra_from_contract_name(
                args, kwargs
            )
            casm_compiled = self.compile_contract_to_casm_from_contract_name(
                args, kwargs
            )

            return casm_compiled, sierra_compiled

    return MockedProjectCompiler()


async def test_declaring_cairo1_contract(
    devnet_gateway_url: str,
    devnet_account: DevnetAccount,
    set_private_key_env_var: SetPrivateKeyEnvVarFixture,
    mocked_project_compiler: ProjectCompiler,
):
    declare = DeclareCairo1Command(
        gateway_facade_factory=GatewayFacadeFactory(Path("")),
        messenger_factory=MessengerFactory(
            log_color_provider=log_color_provider,
            activity_indicator=MagicMock(),
        ),
        project_compiler=mocked_project_compiler,
    )

    args = Namespace(
        chain_id=StarknetChainId.TESTNET,
        account_address=devnet_account.address,
        contract="minimal",
        gateway_url=devnet_gateway_url,
        max_fee=int(1e16),
        wait_for_acceptance=False,
        json=False,
        signer_class=None,
        private_key_path=None,
        network=None,
        token=None,
        block_explorer=None,
    )

    with set_private_key_env_var(devnet_account.private_key):
        response = await declare.run(args)

        assert response.class_hash is not None
