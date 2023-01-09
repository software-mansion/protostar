from typing import Optional

from protostar.starknet.data_transformer import CairoOrPythonData
from protostar.testing.cairo_cheatcodes.cairo_cheatcode import CairoCheatcode
from protostar.testing.cairo_cheatcodes.declare_cairo_cheatcode import (
    DeclareCairoCheatcode,
)
from protostar.testing.cairo_cheatcodes.deploy_cairo_cheatcode import (
    DeployCairoCheatcode,
)
from protostar.testing.cairo_cheatcodes.prepare_cairo_cheatcode import (
    PrepareCairoCheatcode,
)
from protostar.contract_types import DeployedContract


class DeployContractCairoCheatcode(CairoCheatcode):
    def __init__(
        self,
        declare_cheatcode: DeclareCairoCheatcode,
        prepare_cheatcode: PrepareCairoCheatcode,
        deploy_cheatcode: DeployCairoCheatcode,
    ):
        super().__init__()
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
