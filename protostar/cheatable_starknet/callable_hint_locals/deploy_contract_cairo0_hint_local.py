from typing import Optional, Any

from protostar.cairo.short_string import CairoShortString
from protostar.cheatable_starknet.controllers.contracts import DeployedContract
from protostar.starknet.data_transformer import CairoOrPythonData

from .deploy_hint_local import DeployHintLocal
from .declare_cairo0_hint_local import DeclareCairo0HintLocal
from .prepare_hint_local import PrepareHintLocal
from .callable_hint_local import CallableHintLocal


class DeployContractCairo0HintLocal(CallableHintLocal):
    def __init__(
        self,
        declare_cheatcode: DeclareCairo0HintLocal,
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
        return "deploy_contract_cairo0"

    def _build(self):
        return self.deploy_contract_cairo0

    def deploy_contract_cairo0(
        self,
        contract: CairoShortString,
        constructor_args: Optional[CairoOrPythonData] = None,
    ) -> DeployedContract:
        declared_contract = self._declare_cheatcode.declare_cairo0(contract)
        prepared_contract = self._prepare_cheatcode.prepare(
            declared_contract.class_hash, constructor_args
        )
        return self._deploy_cheatcode.deploy_prepared(prepared_contract)
