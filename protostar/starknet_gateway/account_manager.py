from starknet_py.net.signer import BaseSigner
from starknet_py.net import AccountClient, KeyPair
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.client_models import Call as SNCall

from protostar.starknet import Address
from protostar.starknet_gateway.network_config import NetworkConfig

from .multicall import MulticallSignerProtocol, MulticallSignedTransaction, ResolvedCall


class AccountManager(MulticallSignerProtocol):
    def __init__(
        self, private_key: int, address: Address, signer: BaseSigner, gateway_url: str
    ):
        self._private_key = private_key
        self._signer = signer
        gateway_client = GatewayClient(gateway_url)
        self._account_client = AccountClient(
            address=int(address),
            client=gateway_client,
            signer=signer,
            key_pair=KeyPair.from_private_key(private_key),
        )

    async def sign_multicall_transaction(
        self,
        calls: list[ResolvedCall],
    ) -> MulticallSignedTransaction:
        await self._account_client.sign_invoke_transaction(
            calls=[
                SNCall(
                    to_addr=int(call.address),
                    calldata=call.calldata,
                    selector=call.selector,
                )
                for call in calls
            ],
            max_fee=None,
            auto_estimate=True,
            version=1,
        )
        return MulticallSignedTransaction()
