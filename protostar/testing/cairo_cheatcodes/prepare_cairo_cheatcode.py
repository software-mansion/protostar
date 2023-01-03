import collections
from dataclasses import dataclass
from typing import Any, Callable, List, Optional

from starkware.starknet.core.os.contract_address.contract_address import (
    calculate_contract_address_from_hash,
)

from protostar.starknet import CheatcodeException, Address
from protostar.starknet.data_transformer import (
    CairoOrPythonData,
    PythonData,
    from_python_transformer,
    DataTransformerException,
)
from protostar.testing.cairo_cheatcodes.cairo_cheatcode import CairoCheatcode
from protostar.testing.cairo_cheatcodes.declare_cairo_cheatcode import (
    DeclaredContract,
)


@dataclass(frozen=True)
class PreparedContract:
    constructor_calldata: List[int]
    contract_address: int
    class_hash: int
    salt: int


class PrepareCairoCheatcode(CairoCheatcode):
    salt_nonce = 1

    @property
    def name(self) -> str:
        return "prepare"

    def build(self) -> Callable[[Any], Any]:
        return self.prepare

    def prepare(
        self,
        declared: DeclaredContract,
        constructor_calldata: Optional[CairoOrPythonData] = None,
        salt: Optional[int] = None,
    ) -> PreparedContract:
        constructor_calldata = constructor_calldata or []

        if isinstance(constructor_calldata, collections.Mapping):
            constructor_calldata = self.transform_data_to_cairo_format(
                declared.class_hash, constructor_calldata
            )
        contract_salt = PrepareCairoCheatcode.salt_nonce
        PrepareCairoCheatcode.salt_nonce += 1
        if salt is not None:
            contract_salt = salt

        contract_address = calculate_contract_address_from_hash(
            salt=contract_salt,
            class_hash=declared.class_hash,
            constructor_calldata=constructor_calldata,
            deployer_address=0,
        )

        self.cheatable_state.contract_address_to_class_hash_map[
            Address(contract_address)
        ] = declared.class_hash

        return PreparedContract(
            constructor_calldata=constructor_calldata,
            contract_address=contract_address,
            class_hash=declared.class_hash,
            salt=contract_salt,
        )

    def transform_data_to_cairo_format(
        self,
        class_hash: int,
        constructor_calldata: PythonData,
    ) -> List[int]:
        if class_hash not in self.cheatable_state.class_hash_to_contract_abi_map:
            raise CheatcodeException(
                self, f"Couldn't map `class_hash` ({class_hash}) to ({self})."
            )
        contract_abi = self.cheatable_state.class_hash_to_contract_abi_map[class_hash]

        transformer = from_python_transformer(
            contract_abi,
            "constructor",
            "inputs",
        )
        try:
            return transformer(constructor_calldata)
        except DataTransformerException as dt_exc:
            raise CheatcodeException(
                self,
                f"There was an error while parsing constructor arguments:\n{dt_exc.message}",
            ) from dt_exc
