from typing import Any

from protostar.cli import NetworkCommandUtil
from protostar.starknet_gateway import (
    AbiResolver,
    DataTransformerPolicy,
)


async def abi_from_args(args: Any):
    network_command_util = NetworkCommandUtil(args)
    gateway_client = network_command_util.get_gateway_client()
    abi_resolver = AbiResolver(client=gateway_client)
    data_transformer_policy = DataTransformerPolicy(abi_resolver=abi_resolver)
    return await data_transformer_policy.resolve_abi_or_fail(
        address=args.contract_address
    )
