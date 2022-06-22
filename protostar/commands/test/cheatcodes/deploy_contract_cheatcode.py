from typing import Dict, List, Optional, Union

from protostar.commands.test.cheatcodes.cheatcode import Cheatcode
from protostar.commands.test.cheatcodes.declare_cheatcode import DeclareCheatcode
from protostar.commands.test.cheatcodes.deploy_cheatcode import (
    DeployCheatcode,
    DeployedContract,
)
from protostar.commands.test.cheatcodes.prepare_cheatcode import PrepareCheatcode
from protostar.utils.data_transformer_facade import DataTransformerFacade


class DeployContractCheatcode(Cheatcode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._declare_cheatode = DeclareCheatcode(*args, **kwargs)
        self._prepare_cheatode = PrepareCheatcode(*args, **kwargs)
        self._deploy_cheatode = DeployCheatcode(*args, **kwargs)

    @staticmethod
    def name() -> str:
        return "deploy_contract"

    def build(self):
        assert False, "Not implemented"

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
        ],
    ) -> DeployedContract:
        declared_contract = self._declare_cheatode.declare(contract_path)
        prepared_contract = self._prepare_cheatode.prepare(
            declared_contract, constructor_args
        )
        return self._deploy_cheatode.deploy_prepared(prepared_contract)
