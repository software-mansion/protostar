from typing import Optional

from starknet_py.proxy.contract_abi_resolver import (
    ContractAbiResolver,
    ProxyResolutionError,
    ProxyConfig,
)
from starknet_py.net.client import Client
from starknet_py.proxy.proxy_check import (
    OpenZeppelinProxyCheck,
    ArgentProxyCheck,
    ProxyCheck,
)

from protostar.starknet import AbiType, Address

from .call import AbiResolverProtocol


class AbiResolver(AbiResolverProtocol):
    def __init__(self, client: Client) -> None:
        self._client = client

    async def resolve(self, address: Address) -> Optional[AbiType]:
        abi = await self._resolve(
            address=address,
            proxy_checks=[
                OpenZeppelinProxyCheck(),
                ArgentProxyCheck(),
            ],
        )
        if abi:
            return abi
        abi = await self._resolve(address)
        if abi:
            return abi

    async def _resolve(
        self,
        address: Address,
        proxy_checks: Optional[list[ProxyCheck]] = None,
    ) -> Optional[AbiType]:
        try:
            proxy_config = ProxyConfig()
            if proxy_checks:
                proxy_config["proxy_checks"] = proxy_checks
            return await ContractAbiResolver(
                address=int(address),
                client=self._client,
                proxy_config=proxy_config,
            ).resolve()
        except ProxyResolutionError:
            return None
