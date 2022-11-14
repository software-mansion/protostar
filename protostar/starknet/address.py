from typing import Union

from protostar.protostar_exception import ProtostarException


class Address:
    @classmethod
    def from_valid_input(cls, raw_address: Union[str, int]) -> "Address":
        if isinstance(raw_address, int):
            return cls(hex(raw_address))
        numeric_representation = int(raw_address, base=0)
        if numeric_representation < 0:
            raise AddressValidationError(raw_address)
        return cls(hex(int(raw_address, base=0)))

    def __init__(self, hex_value: str) -> None:
        self._hex_value = hex_value

    def as_int(self) -> int:
        return int(self._hex_value, base=16)

    def as_str(self) -> str:
        return f"0x{int(self._hex_value, base=16):064x}"

    def __str__(self) -> str:
        return self.as_str()


class AddressValidationError(ProtostarException):
    def __init__(self, raw_address: Union[int, str]):
        super().__init__(f"Invalid address: {raw_address}")
