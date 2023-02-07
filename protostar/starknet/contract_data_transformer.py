from contextlib import contextmanager

from starknet_py.serialization import (
    serializer_for_function as create_function_serializer,
)
from starknet_py.serialization import CairoSerializerException

from protostar.protostar_exception import ProtostarException

from .selector import Selector
from .contract_abi import ContractAbi
from .data_transformer import CairoData, PythonData


class ContractDataTransformer:
    def __init__(self, contract_abi: ContractAbi) -> None:
        self._contract_abi = contract_abi

    def transform_entrypoint_inputs_to_cairo_data(
        self, selector: Selector, python_data: PythonData
    ) -> CairoData:
        serializer = self._create_entrypoint_serializer(selector)
        with serialization_exception_handler():
            return serializer.serialize(**python_data)

    def transform_entrypoint_outputs_to_python_data(
        self, selector: Selector, cairo_data: CairoData
    ) -> PythonData:
        serializer = self._create_entrypoint_serializer(selector)
        with serialization_exception_handler():
            return serializer.deserialize(cairo_data).as_dict()

    def _create_entrypoint_serializer(self, selector: Selector):
        return create_function_serializer(
            self._contract_abi.unwrap_entrypoint_model(selector)
        )


@contextmanager
def serialization_exception_handler():
    try:
        yield None
    except CairoSerializerException as ex:
        details = ex.args[0] if len(ex.args) > 0 else ""
        raise ProtostarException(
            "Data transformation failed. Did you provide valid data?",
            details=details,
        ) from ex
