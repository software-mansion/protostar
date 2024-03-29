import json
from pathlib import Path
from typing import Union, cast

from marshmallow import ValidationError
from starknet_py.abi import Abi, AbiParsingError, AbiParser
from starknet_py.abi.shape import AbiDictList
from starkware.starknet.public.abi import AbiType

from protostar.protostar_exception import ProtostarException

from .selector import Selector


class ContractAbi:
    def __init__(self, abi_entries: AbiType, contract_abi_model: Abi):
        self._abi_entries = abi_entries
        self._contract_abi_model = contract_abi_model

    @classmethod
    def from_json_file(cls, path: Path):
        potential_abi = json.loads(path.read_text())
        return ContractAbi.from_abi_entries(
            abi_entries=potential_abi,
        )

    @classmethod
    def from_abi_entries(cls, abi_entries: Union[AbiType, AbiDictList]):
        abi_entries = cast(AbiType, abi_entries)
        try:
            contract_abi_model = AbiParser(abi_entries).parse()
            return cls(abi_entries=abi_entries, contract_abi_model=contract_abi_model)
        except (AbiParsingError, ValidationError) as ex:
            raise ProtostarException("Invalid ABI") from ex

    def to_abi_type(self) -> AbiType:
        return self._abi_entries

    def has_constructor(self) -> bool:
        return self._contract_abi_model.constructor is not None

    def unwrap_entrypoint_model(self, selector: Selector):
        fn_name = str(selector)
        if fn_name not in self._contract_abi_model.functions:
            raise ProtostarException(f"Couldn't find {selector} in ABI")
        return self._contract_abi_model.functions[fn_name]
