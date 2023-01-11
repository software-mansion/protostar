from typing import Optional

from protostar.starknet import (
    Address,
    CairoOrPythonData,
    LocalDataTransformationPolicy,
    CairoData,
    ForkableStarknet,
)


class CallTestingUseCase:
    def __init__(
        self,
        local_data_transformation_policy: LocalDataTransformationPolicy,
        starknet: ForkableStarknet,
    ):
        self._local_data_transformation_policy = local_data_transformation_policy
        self._starknet = starknet

    async def execute(
        self,
        contract_address: Address,
        function_name: str,
        calldata: Optional[CairoOrPythonData] = None,
    ) -> CairoData:
        calldata_as_cairo_data = await self._local_data_transformation_policy.transform_calldata_to_cairo_data_by_addr(
            contract_address,
            function_name,
            calldata,
        )
        return await self._starknet.call(
            contract_address,
            function_name,
            calldata_as_cairo_data,
        )
