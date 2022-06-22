import collections
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Union

from starkware.starknet.core.os.contract_address.contract_address import (
    calculate_contract_address_from_hash,
)

from protostar.commands.test.cheatcodes.cheatcode import Cheatcode
from protostar.commands.test.cheatcodes.declare_cheatcode import DeclaredContract
from protostar.commands.test.test_environment_exceptions import CheatcodeException
from protostar.utils.data_transformer_facade import DataTransformerFacade


@dataclass(frozen=True)
class PreparedContract:
    constructor_calldata: List[int]
    contract_address: int
    class_hash: int


class PrepareCheatcode(Cheatcode):
    salt_nonce = 1

    @staticmethod
    def name() -> str:
        return "prepare"

    def build(self) -> Callable[[Any], Any]:
        return self.prepare

    def prepare(
        self,
        declared: DeclaredContract,
        constructor_calldata: Optional[
            Union[
                List[int],
                Dict[
                    DataTransformerFacade.ArgumentName,
                    DataTransformerFacade.SupportedType,
                ],
            ]
        ] = None,
    ) -> PreparedContract:
        constructor_calldata = constructor_calldata or []

        if isinstance(constructor_calldata, collections.Mapping):
            constructor_calldata = self.transform_data_to_cairo_format(
                declared.class_hash, constructor_calldata
            )

        contract_address: int = calculate_contract_address_from_hash(
            salt=PrepareCheatcode.salt_nonce,
            class_hash=declared.class_hash,
            constructor_calldata=constructor_calldata,
            deployer_address=self.contract_address,
        )
        self.state.contract_address_to_class_hash_map[
            contract_address
        ] = declared.class_hash
        PrepareCheatcode.salt_nonce += 1
        return PreparedContract(
            constructor_calldata, contract_address, declared.class_hash
        )

    def transform_data_to_cairo_format(
        self,
        class_hash: int,
        constructor_calldata: Dict[
            DataTransformerFacade.ArgumentName,
            DataTransformerFacade.SupportedType,
        ],
    ) -> List[int]:
        if class_hash not in self.state.class_hash_to_contract_path_map:
            raise CheatcodeException(
                self.name(), f"Couldn't map `class_hash` ({class_hash}) to ({self})."
            )
        contract_path = self.state.class_hash_to_contract_path_map[class_hash]

        return self.data_transformer.build_from_python_transformer(
            contract_path,
            "constructor",
            "inputs",
        )(constructor_calldata)
