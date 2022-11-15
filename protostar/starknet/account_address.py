from typing import Optional, Sequence

from starkware.starknet.core.os.contract_address.contract_address import (
    calculate_contract_address_from_hash,
)

from .address import Address


class AccountAddress(Address):
    @classmethod
    def from_class_hash(
        cls,
        class_hash: int,
        salt: int,
        constructor_calldata: Sequence[int],
        deployer_address: Optional[Address] = None,
    ) -> "AccountAddress":
        address = calculate_contract_address_from_hash(
            class_hash=class_hash,
            constructor_calldata=constructor_calldata,
            salt=salt,
            deployer_address=int(deployer_address) if deployer_address else 0,
        )
        return AccountAddress.from_user_input(address)
