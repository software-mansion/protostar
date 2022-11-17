from typing import Optional, Sequence, Union

from typing_extensions import Self
from starkware.starknet.core.os.contract_address.contract_address import (
    calculate_contract_address_from_hash,
)

from protostar.protostar_exception import ProtostarException

RawAddress = Union[str, int]


class Address:
    @classmethod
    def from_class_hash(
        cls,
        class_hash: int,
        salt: int,
        constructor_calldata: Sequence[int],
        deployer_address: Optional["Address"] = None,
    ) -> Self:
        address = calculate_contract_address_from_hash(
            class_hash=class_hash,
            constructor_calldata=constructor_calldata,
            salt=salt,
            deployer_address=int(deployer_address) if deployer_address else 0,
        )
        return cls(address)

    @classmethod
    def from_user_input(cls, raw_address: RawAddress) -> Self:
        try:
            value = (
                raw_address
                if isinstance(raw_address, int)
                else int(raw_address, base=0)
            )
        except ValueError as err:
            raise AddressValidationError(raw_address) from err
        if value < 0:
            raise AddressValidationError(raw_address)
        return cls(value)

    def __init__(self, value: int) -> None:
        self._value = value

    def __str__(self) -> str:
        return f"0x{self._value:064x}"

    def __int__(self) -> int:
        return self._value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Address):
            return self._value == int(other)
        if isinstance(other, str):
            return self._value == int(other, base=0)
        if isinstance(other, int):
            return self._value == other
        return False

    def __hash__(self) -> int:
        return self._value


class AddressValidationError(ProtostarException):
    def __init__(self, raw_address: Union[int, str]):
        super().__init__(f"Invalid address: {raw_address}")
