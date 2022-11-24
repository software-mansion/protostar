from typing import Optional

from starknet_py.net.client import Client
from starknet_py.contract import Contract, ContractFunction
from starknet_py.proxy.contract_abi_resolver import ProxyResolutionError
from starknet_py.net.client_errors import ClientError, ContractNotFoundError

from protostar.protostar_exception import ProtostarException
from protostar.starknet import Address


class ContractFunctionFactory:
    def __init__(self, default_client: Client) -> None:
        self._default_client = default_client

    async def create(
        self,
        address: Address,
        function_name: str,
        client: Optional[Client] = None,
    ) -> ContractFunction:
        contract = await self._create_contract(address, client or self._default_client)
        try:
            return contract.functions[function_name]
        except KeyError:
            raise UnknownFunctionException(function_name) from KeyError

    async def _create_contract(self, address: Address, client: Client):
        try:
            return await self._create_contract_from_possibly_proxy_address(
                address, client
            )
        except ContractNotFoundError as err:
            raise ContractNotFoundException(address) from err

    async def _create_contract_from_possibly_proxy_address(
        self,
        contract_address: Address,
        client: Client,
    ) -> Contract:
        try:
            return await self._create_contract_from_proxy_address(
                contract_address, client
            )
        except ProxyResolutionError:
            return await Contract.from_address(
                address=int(contract_address),
                client=client or self._default_client,
                proxy_config=False,
            )

    async def _create_contract_from_proxy_address(
        self, contract_address: Address, client: Client
    ) -> Contract:
        try:
            return await Contract.from_address(
                address=int(contract_address),
                client=client,
                proxy_config=True,
            )
        except ClientError as err:
            if "not deployed" in err.message:
                raise ContractNotFoundException(
                    contract_address=contract_address
                ) from err
            raise err


class UnknownFunctionException(ProtostarException):
    def __init__(self, function_name: str):
        super().__init__(f"Tried to call unknown function: '{function_name}'")


class ContractNotFoundException(ProtostarException):
    def __init__(self, contract_address: Address):
        super().__init__(f"Tried to call unknown contract:\n{contract_address}")
