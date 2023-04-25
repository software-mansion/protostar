import asyncio
from typing import Awaitable

from starknet_py.net.client_errors import ClientError
from starknet_py.net.client_models import Call
from starknet_py.net.gateway_client import GatewayClient
from starkware.starknet.public.abi import (
    get_selector_from_name,
    VALIDATE_ENTRY_POINT_NAME,
)

from protostar.starknet import Address


class AccountTxVersionDetector:
    """
    Tries to infer what Starknet transaction version an account contract supports,
    by probing its behaviour via a call.

    This class has a built-in permanent cache, keyed by account address.
    """

    def __init__(self, client: GatewayClient):
        self._client = client
        self._cache: dict[Address, Awaitable[int]] = {}

    async def detect(self, account_address: Address) -> int:
        cached = self._cache.get(account_address)
        if cached is not None:
            return await cached
        future = asyncio.ensure_future(self._do_detect(account_address))
        self._cache[account_address] = future
        return await future

    async def _do_detect(self, account_address: Address) -> int:
        try:
            await self._client.call_contract(
                Call(
                    to_addr=int(account_address),
                    selector=get_selector_from_name(VALIDATE_ENTRY_POINT_NAME),
                    calldata=[0, 0, 0, 0],
                )
            )

            return 1
        except ClientError as ex:
            if (
                ex.code == "500"
                and "Entry point" in ex.message
                and "not found in contract with class hash" in ex.message
            ):
                return 0

            if ex.code == "500":
                return 1

            raise
