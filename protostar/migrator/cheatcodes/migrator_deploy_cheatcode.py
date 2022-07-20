import asyncio

from protostar.commands.test.cheatcodes.deploy_cheatcode import DeployedContract
from protostar.migrator.cheatcodes.migrator_prepare_cheatcode import (
    MigratorPreparedContract,
)
from protostar.starknet.cheatcode import Cheatcode
from protostar.starknet_gateway.gateway_facade import GatewayFacade


class MigratorDeployCheatcode(Cheatcode):
    def __init__(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        gateway_facade: GatewayFacade,
    ):
        super().__init__(syscall_dependencies)
        self._gateway_facade = gateway_facade

    @property
    def name(self) -> str:
        return "deploy"

    def build(self):
        return self._deploy_prepared

    def _deploy_prepared(self, prepared: MigratorPreparedContract) -> DeployedContract:
        response = asyncio.run(
            self._gateway_facade.deploy(
                compiled_contract_path=prepared.declared_contract.contract_path,
                gateway_url=prepared.declared_contract.config.gateway_url,
                inputs=prepared.constructor_calldata,
                token=prepared.declared_contract.config.token,
            )
        )

        return DeployedContract(contract_address=response.address)
