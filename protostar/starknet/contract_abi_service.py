import json
from pathlib import Path

from starknet_py.abi import Abi, AbiParsingError, AbiParser
from starkware.starknet.public.abi import AbiType

from protostar.protostar_exception import ProtostarException
from protostar.starknet import Selector


class ContractAbiService:
    @classmethod
    def from_json_file(cls, path: Path):
        assert path.suffix == ".json"
        potential_abi = json.loads(path.read_text())
        return ContractAbiService.from_contract_abi(
            contract_abi=potential_abi,
        )

    @classmethod
    def from_contract_abi(cls, contract_abi: AbiType):
        contract_abi_model = AbiParser(contract_abi).parse()
        try:
            return cls(contract_abi=contract_abi, contract_abi_model=contract_abi_model)
        except AbiParsingError as ex:
            raise ProtostarException("Invalid ABI") from ex

    def __init__(self, contract_abi: list[dict], contract_abi_model: Abi):
        self._contract_abi = contract_abi
        self._contract_abi_model = contract_abi_model

    def has_constructor(self) -> bool:
        return self._contract_abi_model.constructor is not None

    def has_entrypoint_parameters(self, selector: Selector) -> bool:
        fn_name_abi = self.get_entrypoint_model_or_panic(selector)
        return len(fn_name_abi.inputs) > 0

    def get_entrypoint_model_or_panic(self, selector: Selector):
        fn_name = str(selector)
        if fn_name not in self._contract_abi_model.functions:
            raise ProtostarException(f"Couldn't find {selector} in ABI")
        return self._contract_abi_model.functions[fn_name]
