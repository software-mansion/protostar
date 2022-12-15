from typing import Optional, Protocol

from protostar.starknet import (
    HumanDataRepresentation,
    Address,
    Calldata,
    Selector,
    AbiType,
    CairoDataRepresentation,
)


class DataTransformerProtocol(Protocol):
    async def transform_calldata_if_necessary(
        self,
        calldata: Optional[Calldata],
        address: Address,
        selector: Selector,
        abi: Optional[AbiType],
    ) -> CairoDataRepresentation:
        ...

    async def try_transforming_entrypoint_output(
        self,
        data: CairoDataRepresentation,
        address: Address,
        selector: Selector,
        abi: Optional[AbiType],
    ) -> Optional[HumanDataRepresentation]:
        ...
