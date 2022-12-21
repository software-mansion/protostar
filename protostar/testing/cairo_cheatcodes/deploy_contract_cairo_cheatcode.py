from typing import Optional, Any

from protostar.starknet.data_transformer import CairoOrPythonData
from protostar.testing.cairo_cheatcodes.cairo_cheatcode import CairoCheatcode
from protostar.testing.cairo_cheatcodes.declare_contract_cairo_cheatcode import (
    DeclareContractCairoCheatcode,
)
from protostar.testing.cairo_cheatcodes.deploy_cairo_cheatcode import (
    DeployCairoCheatcode,
    DeployedContract,
)
from protostar.testing.cairo_cheatcodes.prepare_deployment_cairo_cheatcode import (
    PrepareDeploymentCairoCheatcode,
)


class DeployContractCairoCheatcode(CairoCheatcode):
    def __init__(
        self,
        declare_cheatcode: DeclareContractCairoCheatcode,
        prepare_cheatcode: PrepareDeploymentCairoCheatcode,
        deploy_cheatcode: DeployCairoCheatcode,
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

    def build(self):
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
