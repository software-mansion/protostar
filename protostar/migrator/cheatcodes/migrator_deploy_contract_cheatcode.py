import asyncio
import collections
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any

from protostar.commands.test.cheatcodes.deploy_cheatcode import DeployedContract
from protostar.commands.test.cheatcodes.deploy_contract_cheatcode import (
    DeployContractCheatcodeProtocol,
)
from protostar.starknet.cheatcode import Cheatcode
from protostar.starknet_gateway.gateway_facade import GatewayFacade
from protostar.utils.data_transformer import CairoOrPythonData
from protostar.commands.test.test_environment_exceptions import (
    KeywordOnlyArgumentCheatcodeException,
)


class MigratorDeployContractCheatcode(Cheatcode):
    @dataclass
    class Config:
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
        *args,
        config: Optional[Dict[str, Any]] = None,
    ) -> DeployedContract:
        if len(args) > 0:
            raise KeywordOnlyArgumentCheatcodeException(self.name, ["config"])

        if isinstance(constructor_args, collections.Mapping):
            assert False, "Data Transformer is not supported"

        if not config:
            config = {}
        config = collections.defaultdict(lambda: None, config)

        response = asyncio.run(
            self._gateway_facade.deploy(
                compiled_contract_path=Path(contract_path),
                inputs=constructor_args,
                token=self._config.token,
                wait_for_acceptance=config["wait_for_acceptance"] or False,
            )
        )

        return DeployedContract(contract_address=response.address)
