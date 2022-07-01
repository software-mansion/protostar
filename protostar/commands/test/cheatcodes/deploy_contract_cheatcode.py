from typing import Any, Callable, Dict, List, Optional, Union

from protostar.commands.test.cheatcodes.declare_cheatcode import DeclareCheatcode
from protostar.commands.test.cheatcodes.deploy_cheatcode import (
    DeployCheatcode,
    DeployedContract,
)
from protostar.commands.test.cheatcodes.prepare_cheatcode import PrepareCheatcode
from protostar.commands.test.starkware.cheatcode import Cheatcode
from protostar.utils.data_transformer_facade import DataTransformerFacade


class DeployContractCheatcode(Cheatcode):
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        syscall_dependencies: Cheatcode.SyscallDependencies,
        declare_cheatcode: DeclareCheatcode,
        prepare_cheatcode: PrepareCheatcode,
        deploy_cheatcode: DeployCheatcode,
    ):
        super().__init__(syscall_dependencies)
        self._declare_cheatcode = declare_cheatcode
        self._prepare_cheatcode = prepare_cheatcode
        self._deploy_cheatcode = deploy_cheatcode

    @property
    def name(self) -> str:
        return "deploy_contract"

    def build(self) -> Callable[..., Any]:
        return self.deploy_contract

    def deploy_contract(
        self,
        contract_path: str,
        constructor_args: Optional[
            Union[
                List[int],
                Dict[
                    DataTransformerFacade.ArgumentName,
                    DataTransformerFacade.SupportedType,
                ],
            ]
        ] = None,
    ) -> DeployedContract:
        declared_contract = self._declare_cheatcode.declare(contract_path)
        prepared_contract = self._prepare_cheatcode.prepare(
            declared_contract, constructor_args
        )
        return self._deploy_cheatcode.deploy_prepared(prepared_contract)
