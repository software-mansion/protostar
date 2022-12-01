from typing import Union

from starknet_py.net.client_models import TransactionStatus
from starknet_py.net.gateway_client import GatewayClient

from tests._conftest.devnet.devnet_account import DevnetAccount
from protostar.starknet_gateway.gateway_facade import Wei
from tests._conftest.devnet.devnet_account_preparator import DevnetAccountPreparator


class DevnetFixture:
    def __init__(
        self,
        gas_price: Wei,
        devnet_gateway_url: str,
        devnet_account_preparator: DevnetAccountPreparator,
        predeployed_accounts: list[DevnetAccount],
    ) -> None:
        self._gas_price = gas_price
        self._devnet_gateway_url = devnet_gateway_url
        self._gateway_client = GatewayClient(devnet_gateway_url)
        self._devnet_account_preparator = devnet_account_preparator
        self._predeployed_accounts = predeployed_accounts

    async def prepare_account(self, salt: int, private_key: int):
        return await self._devnet_account_preparator.prepare(
            salt=salt, private_key=private_key
        )

    async def assert_transaction_accepted(self, transaction_hash: Union[str, int]):
        (_, transaction_status) = await self._gateway_client.wait_for_tx(
            transaction_hash, wait_for_accept=True
        )
        assert transaction_status == TransactionStatus.ACCEPTED_ON_L2

    def get_gateway_url(self) -> str:
        return self._devnet_gateway_url

    def get_predeployed_accounts(self) -> list[DevnetAccount]:
        return self._predeployed_accounts

    def get_gas_price(self):
        return self._gas_price
