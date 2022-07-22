import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from protostar.commands.test.cheatcodes.deploy_cheatcode import DeployedContract
from protostar.starknet.cheatcode import Cheatcode
from protostar.starknet_gateway.gateway_facade import GatewayFacade


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

    def build(self):
        return self._deploy_contract

    def _deploy_contract(
        self,
        contract_path: str,
        constructor_args: Optional[List[int]] = None,
    ) -> DeployedContract:
        response = asyncio.run(
            self._gateway_facade.deploy(
                compiled_contract_path=Path(contract_path),
                inputs=constructor_args,
                gateway_url=self._config.gateway_url,
                token=self._config.token,
            )
        )

        return DeployedContract(contract_address=response.address)
