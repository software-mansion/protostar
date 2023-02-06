from typing import Optional, Any

from protostar.cheatable_starknet.callable_hint_locals.callable_hint_local import (
    CallableHintLocal,
)
from protostar.cheatable_starknet.callable_hint_locals.declare_hint_local import (
    DeclareHintLocal,
)
from protostar.cheatable_starknet.callable_hint_locals.deploy_hint_local import (
    DeployHintLocal,
)
from protostar.cheatable_starknet.callable_hint_locals.prepare_hint_local import (
    PrepareHintLocal,
)
from protostar.starknet.data_transformer import CairoOrPythonData
from protostar.contract_types import DeployedContract


class DeployContractHintLocal(CallableHintLocal):
    def __init__(
        self,
        declare_cheatcode: DeclareHintLocal,
        prepare_cheatcode: PrepareHintLocal,
        deploy_cheatcode: DeployHintLocal,
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        self._declare_cheatcode = declare_cheatcode
        self._prepare_cheatcode = prepare_cheatcode
        self._deploy_cheatcode = deploy_cheatcode

    @property
    def name(self) -> str:
        return "deploy_contract"

    def _build(self):
        return self.deploy_contract

    def deploy_contract(
        self,
        contract: str,
        constructor_args: Optional[CairoOrPythonData] = None,
    ) -> DeployedContract:
        declared_contract = self._declare_cheatcode.declare(contract)
        prepared_contract = self._prepare_cheatcode.prepare(
            declared_contract, constructor_args
        )
        return self._deploy_cheatcode.deploy_prepared(prepared_contract)
