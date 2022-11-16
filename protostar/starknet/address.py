from typing import Union

from typing_extensions import Self

from protostar.protostar_exception import ProtostarException


class Address:
    @classmethod
    def from_user_input(cls, raw_address: Union[str, int]) -> Self:
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


class AddressValidationError(ProtostarException):
    def __init__(self, raw_address: Union[int, str]):
        super().__init__(f"Invalid address: {raw_address}")
