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

from protostar.starknet import Address, ContractAbi


class AbiResolver:
    def __init__(self, client: Client) -> None:
        self._client = client

    async def resolve(self, address: Address) -> Optional[ContractAbi]:
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
    ) -> Optional[ContractAbi]:
        try:
            proxy_config = ProxyConfig()
            if proxy_checks:
                proxy_config["proxy_checks"] = proxy_checks
            abi = await ContractAbiResolver(
                address=int(address),
                client=self._client,
                proxy_config=proxy_config,
            ).resolve()
            return ContractAbi.from_abi_entries(abi)
        except ProxyResolutionError:
            return None
