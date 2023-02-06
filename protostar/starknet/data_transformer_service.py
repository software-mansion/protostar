from starknet_py.serialization import (
    serializer_for_function as create_function_serializer,
)

from protostar.starknet import Selector

from .contract_abi_service import ContractAbiService
from .data_transformer import CairoData, PythonData


class DataTransformerService:
    def __init__(self, contract_abi_service: ContractAbiService) -> None:
        self._contract_abi_service = contract_abi_service

    def transform_entrypoint_inputs_to_cairo_data(
        self, selector: Selector, python_data: PythonData
    ) -> CairoData:
        serializer = self._create_entrypoint_serializer(selector)
        return serializer.serialize(**python_data)

    def transform_entrypoint_outputs_to_python_data(
        self, selector: Selector, cairo_data: CairoData
    ) -> PythonData:
        serializer = self._create_entrypoint_serializer(selector)
        return serializer.deserialize(cairo_data).as_dict()

    def _create_entrypoint_serializer(self, selector: Selector):
        return create_function_serializer(
            self._contract_abi_service.get_entrypoint_model_or_panic(selector)
        )
