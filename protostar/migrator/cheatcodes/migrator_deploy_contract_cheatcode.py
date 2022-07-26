import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from protostar.commands.test.cheatcodes.deploy_cheatcode import DeployedContract
from protostar.commands.test.cheatcodes.deploy_contract_cheatcode import (
    DeployContractCheatcodeProtocol,
)
from protostar.starknet.cheatcode import Cheatcode
from protostar.starknet_gateway.gateway_facade import GatewayFacade
from protostar.utils.data_transformer import CairoOrPythonData


class MigratorDeployContractCheatcode(Cheatcode):
    @dataclass
    class Config:
        gateway_url: str
        token: Optional[str]

    def __init__(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        gateway_facade: GatewayFacade,
        config: Config,
    ):
        super().__init__(syscall_dependencies)
        self._gateway_facade = gateway_facade
        self._config = config

    @property
    def name(self) -> str:
        return "deploy_contract"

    def build(self) -> DeployContractCheatcodeProtocol:
        return self._deploy_contract

    def _deploy_contract(
        self,
        contract_path: str,
        constructor_args: Optional[CairoOrPythonData] = None,
    ) -> DeployedContract:
        # TODO: assert constructor_args

        response = asyncio.run(
            self._gateway_facade.deploy(
                compiled_contract_path=Path(contract_path),
                inputs=constructor_args,
                gateway_url=self._config.gateway_url,
                token=self._config.token,
            )
        )

        return DeployedContract(contract_address=response.address)
