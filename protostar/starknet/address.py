from typing import Union

from typing_extensions import Self

from protostar.protostar_exception import ProtostarException


class Address:
    @classmethod
    def from_user_input(cls, raw_address: Union[str, int]) -> Self:
        if isinstance(raw_address, int):
            return cls(raw_address)
        numeric_representation = int(raw_address, base=0)
        if numeric_representation < 0:
            raise AddressValidationError(raw_address)
        return cls(int(raw_address, base=0))

    def __init__(self, value: int) -> None:
        self._value = value

    def as_int(self) -> int:
        return self._value

    def as_str(self) -> str:
        return f"0x{self._value:064x}"

    def __str__(self) -> str:
        return self.as_str()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Address):
            return self._value == other.as_int()
        if isinstance(other, str):
            return self._value == int(other, base=0)
        if isinstance(other, int):
            return self._value == other
        return False


class AddressValidationError(ProtostarException):
    def __init__(self, raw_address: Union[int, str]):
        super().__init__(f"Invalid address: {raw_address}")
